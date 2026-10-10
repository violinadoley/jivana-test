import logging
from typing import Protocol

from app.core.config import Settings
from app.core.exceptions import DocumentAIConfigurationError
from app.schemas.meddocs import BoundingBox, EvidenceStatus, SourceBlock

logger = logging.getLogger(__name__)


class DocumentAIClient(Protocol):
    def verify_processor(self) -> None: ...

    def process_to_blocks(
        self, document_id: str, content: bytes, mime_type: str
    ) -> list[SourceBlock]: ...


class DocumentAIService:
    def __init__(self, settings: Settings, client: DocumentAIClient | None = None) -> None:
        self._settings = settings
        self._client = client

    @property
    def is_configured(self) -> bool:
        return self._settings.document_ai_configured

    def _get_client(self) -> DocumentAIClient:
        if self._client is not None:
            return self._client
        if not self.is_configured:
            raise DocumentAIConfigurationError("Document AI processor is not configured.")
        return _LiveDocumentAIClient(self._settings)

    def verify_processor_if_configured(self) -> None:
        if not self.is_configured:
            return
        self._get_client().verify_processor()

    def process_to_blocks(
        self, document_id: str, content: bytes, mime_type: str
    ) -> list[SourceBlock]:
        if not self.is_configured:
            return []
        return self._get_client().process_to_blocks(document_id, content, mime_type)


class _LiveDocumentAIClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def verify_processor(self) -> None:
        processor = (self._settings.document_ai_processor_id or "").strip()
        location = self._settings.document_ai_location
        project = self._settings.effective_gcp_project_id
        if not processor or not project:
            raise DocumentAIConfigurationError("Document AI processor or project id missing.")
        try:
            from google.cloud import documentai

            client = documentai.DocumentProcessorServiceClient()
            name = (
                processor
                if processor.startswith("projects/")
                else client.processor_path(project, location, processor)
            )
            client.get_processor(name=name)
        except DocumentAIConfigurationError:
            raise
        except Exception as exc:
            logger.exception("Document AI processor verification failed")
            raise DocumentAIConfigurationError(
                "Document AI processor invalid or inaccessible in configured region."
            ) from exc

    def process_to_blocks(
        self, document_id: str, content: bytes, mime_type: str
    ) -> list[SourceBlock]:
        from google.cloud import documentai

        client = documentai.DocumentProcessorServiceClient()
        processor = self._settings.document_ai_processor_id or ""
        project = self._settings.effective_gcp_project_id or ""
        location = self._settings.document_ai_location
        name = (
            processor
            if processor.startswith("projects/")
            else client.processor_path(project, location, processor)
        )
        raw = documentai.RawDocument(content=content, mime_type=mime_type)
        request = documentai.ProcessRequest(name=name, raw_document=raw)
        result = client.process_document(request=request)
        blocks: list[SourceBlock] = []
        idx = 0
        for page in result.document.pages:
            page_num = page.page_number or 1
            for paragraph in page.paragraphs or []:
                text = _layout_text(paragraph.layout, result.document.text)
                if not text.strip():
                    continue
                idx += 1
                bbox = _layout_bbox(paragraph.layout)
                blocks.append(
                    SourceBlock(
                        source_block_id=f"{document_id}:p{page_num}:b{idx}",
                        document_id=document_id,
                        page_number=page_num,
                        text=text,
                        bounding_box=bbox,
                        confidence=0.9,
                        evidence_status=EvidenceStatus.VERIFIED,
                    )
                )
        if not blocks and result.document.text:
            blocks.append(
                SourceBlock(
                    source_block_id=f"{document_id}:p1:b1",
                    document_id=document_id,
                    page_number=1,
                    text=result.document.text[:2000],
                    confidence=0.7,
                    evidence_status=EvidenceStatus.LOW,
                )
            )
        return blocks


def _layout_text(layout: object, full_text: str) -> str:
    text_anchor = getattr(layout, "text_anchor", None)
    if not text_anchor or not getattr(text_anchor, "text_segments", None):
        return ""
    parts: list[str] = []
    for segment in text_anchor.text_segments:
        start = int(getattr(segment, "start_index", 0) or 0)
        end = int(getattr(segment, "end_index", 0) or 0)
        parts.append(full_text[start:end])
    return "".join(parts)


def _layout_bbox(layout: object) -> BoundingBox | None:
    bounding_poly = getattr(layout, "bounding_poly", None)
    if not bounding_poly or not getattr(bounding_poly, "normalized_vertices", None):
        return None
    verts = bounding_poly.normalized_vertices
    if not verts:
        return None
    xs = [v.x for v in verts if v.x is not None]
    ys = [v.y for v in verts if v.y is not None]
    if not xs or not ys:
        return None
    x0, x1 = min(xs), max(xs)
    y0, y1 = min(ys), max(ys)
    return BoundingBox(x=x0, y=y0, width=max(x1 - x0, 0), height=max(y1 - y0, 0))
