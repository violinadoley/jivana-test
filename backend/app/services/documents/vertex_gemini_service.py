import json
import logging
from typing import Protocol

from app.core.config import Settings
from app.core.exceptions import MeddocsProcessingError
from app.schemas.meddocs import DocumentType, SourceBlock, VertexExtractOutput, VertexFieldOutput

logger = logging.getLogger(__name__)


class VertexMeddocsClient(Protocol):
    def extract(
        self,
        document_id: str,
        blocks: list[SourceBlock],
        filename: str,
    ) -> VertexExtractOutput: ...


class VertexGeminiMeddocsService:
    def __init__(self, settings: Settings, client: VertexMeddocsClient | None = None) -> None:
        self._settings = settings
        self._client = client

    def extract(
        self,
        document_id: str,
        blocks: list[SourceBlock],
        filename: str,
    ) -> VertexExtractOutput:
        if self._client is not None:
            return self._client.extract(document_id, blocks, filename)
        return _LiveVertexClient(self._settings).extract(document_id, blocks, filename)


class _LiveVertexClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def extract(
        self,
        document_id: str,
        blocks: list[SourceBlock],
        filename: str,
    ) -> VertexExtractOutput:
        project = self._settings.effective_gcp_project_id
        if not project:
            raise MeddocsProcessingError("GCP project id required for Vertex MedDocs extraction.")

        from google import genai

        client = genai.Client(
            vertexai=True,
            project=project,
            location=self._settings.gcp_location,
        )
        catalog_json = [
            {
                "source_block_id": b.source_block_id,
                "page_number": b.page_number,
                "text": b.text[:500],
            }
            for b in blocks
        ]
        prompt = (
            "You extract structured medical admin document fields. "
            "Return JSON only with keys: document_type (one of prior_medication_record, "
            "discharge_summary, current_prescription, unknown), classification_confidence, "
            "fields (list of {name, value, source_block_ids}), medications (list of "
            "{medication_name, strength, dose, route, frequency, source_block_ids}). "
            "Use ONLY source_block_ids from the catalog. No treatment recommendations.\n"
            f"filename: {filename}\n"
            f"catalog: {json.dumps(catalog_json)}"
        )
        try:
            response = client.models.generate_content(
                model=self._settings.vertex_model,
                contents=prompt,
                config={"response_mime_type": "application/json"},
            )
        except Exception as exc:
            logger.exception("Vertex extraction failed")
            raise MeddocsProcessingError("Vertex document extraction failed.") from exc

        text = getattr(response, "text", None) or "{}"
        return _parse_vertex_json(text)


def _parse_vertex_json(text: str) -> VertexExtractOutput:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise MeddocsProcessingError("Vertex returned invalid JSON.") from exc

    doc_type_raw = str(data.get("document_type", "unknown"))
    try:
        doc_type = DocumentType(doc_type_raw)
    except ValueError:
        doc_type = DocumentType.UNKNOWN

    fields = [
        VertexFieldOutput(
            name=str(f.get("name", "")),
            value=f.get("value"),
            source_block_ids=list(f.get("source_block_ids") or []),
        )
        for f in data.get("fields") or []
        if f.get("name")
    ]
    return VertexExtractOutput(
        document_type=doc_type,
        classification_confidence=float(data.get("classification_confidence") or 0),
        fields=fields,
        medications=list(data.get("medications") or []),
    )
