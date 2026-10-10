import hashlib
import logging
import uuid
from datetime import UTC, datetime

from app.core.config import Settings
from app.core.exceptions import (
    DocumentAIConfigurationError,
    FileUploadError,
)
from app.schemas.meddocs import (
    DocumentMeta,
    EvidenceStatus,
    ExtractedField,
    JobMetrics,
    JobStatus,
    MedicationLine,
    MedReconciliationJob,
    SourceBlock,
    SourceRef,
    ValidationFinding,
)
from app.services.documents.document_ai_service import DocumentAIService
from app.services.documents.document_store import DocumentStore
from app.services.documents.job_status import apply_status_to_job
from app.services.documents.med_reconciler import ReconcileInput, reconcile_medications
from app.services.documents.module2_export import on_reconciliation_completed
from app.services.documents.normalizers import normalize_medication_name
from app.services.documents.source_block_catalog import SourceBlockCatalog
from app.services.documents.source_block_resolver import resolve_vertex_output
from app.services.documents.text_extract import extract_text_pages
from app.services.documents.vertex_gemini_service import VertexGeminiMeddocsService
from app.services.storage.storage_service import ALLOWED_CONTENT_TYPES, StorageService

logger = logging.getLogger(__name__)


class UploadedPart:
    def __init__(self, filename: str, content_type: str, data: bytes) -> None:
        self.filename = filename
        self.content_type = content_type
        self.data = data


class MeddocsIntakePipeline:
    def __init__(
        self,
        settings: Settings,
        storage: StorageService,
        store: DocumentStore,
        document_ai: DocumentAIService,
        vertex: VertexGeminiMeddocsService,
    ) -> None:
        self._settings = settings
        self._storage = storage
        self._store = store
        self._document_ai = document_ai
        self._vertex = vertex

    def run_reconciliation(
        self,
        files: list[UploadedPart],
        owner_uid: str | None,
        expected_hashes: set[str] | None = None,
    ) -> MedReconciliationJob:
        if len(files) < 1 or len(files) > 3:
            raise FileUploadError("Upload 1 to 3 documents for reconciliation.")

        started = datetime.now(UTC)
        job_id = uuid.uuid4().hex
        job = MedReconciliationJob(
            job_id=job_id,
            owner_uid=owner_uid,
            status=JobStatus.PROCESSING,
            metrics=JobMetrics(started_at=started.isoformat()),
        )
        self._store.save_job(job)

        try:
            self._document_ai.verify_processor_if_configured()
        except DocumentAIConfigurationError as exc:
            job.status = JobStatus.FAILED
            job.error_code = exc.code
            job.error_message = exc.message
            self._store.update_job(job)
            raise

        seen_hashes: set[str] = set(expected_hashes or [])
        catalog = SourceBlockCatalog()
        reconcile_input = ReconcileInput()

        for part in files:
            self._validate_upload(part)
            content_hash = hashlib.sha256(part.data).hexdigest()
            if content_hash in seen_hashes:
                job.validation_findings.append(
                    ValidationFinding(
                        code="DUPLICATE_DOCUMENT",
                        message=f"Duplicate upload detected for {part.filename}.",
                        requires_review=True,
                    )
                )
            seen_hashes.add(content_hash)

            doc_id = uuid.uuid4().hex[:12]
            meta = DocumentMeta(
                document_id=doc_id,
                filename=part.filename,
                content_type=part.content_type,
                content_hash=content_hash,
            )
            if self._storage.storage_configured:
                uploaded = self._storage.upload(part.data, part.filename, part.content_type)
                meta.storage_key = uploaded.storage_key
            job.documents.append(meta)

            blocks = self._build_blocks(doc_id, part, job)
            for block in blocks:
                catalog.add_block(block)

            vertex_out = self._vertex.extract(doc_id, blocks, part.filename)
            meta.document_type = vertex_out.document_type
            reconcile_input.document_types[doc_id] = vertex_out.document_type

            resolved = resolve_vertex_output(doc_id, catalog, vertex_out)
            job.validation_findings.extend(resolved.findings)
            if resolved.weak_evidence_used:
                job.reconciliation_used_weak_evidence = True

            id_fields: dict[str, str | None] = {}
            for field in resolved.fields:
                job.metrics.extraction_field_count += 1
                if field.name in ("mrn", "patient_name"):
                    id_fields[field.name] = field.value
            reconcile_input.identifier_fields[doc_id] = id_fields

            meds = _medications_from_vertex(doc_id, catalog, vertex_out, resolved.fields)
            job.medications_by_document[doc_id] = meds
            reconcile_input.medications_by_document[doc_id] = meds

            if any("documented change" in b.text.lower() for b in blocks):
                reconcile_input.discharge_has_documented_change_hint = True

        recon = reconcile_medications(reconcile_input)
        job.discrepancies.extend(recon.discrepancies)
        job.validation_findings.extend(recon.findings)
        if recon.weak_evidence_used:
            job.reconciliation_used_weak_evidence = True

        finished = datetime.now(UTC)
        job.metrics.completed_at = finished.isoformat()
        job.metrics.processing_ms = int((finished - started).total_seconds() * 1000)
        job.metrics.validation_issue_count = len(job.validation_findings)
        job.metrics.discrepancy_count = len(job.discrepancies)

        apply_status_to_job(job)
        self._store.update_job(job)
        if job.status == JobStatus.COMPLETED:
            on_reconciliation_completed(job)
        return job

    def _validate_upload(self, part: UploadedPart) -> None:
        if part.content_type not in ALLOWED_CONTENT_TYPES:
            raise FileUploadError("Unsupported file type.")
        if len(part.data) > self._settings.max_upload_size_bytes:
            raise FileUploadError("File exceeds maximum size.")
        if not part.data:
            raise FileUploadError("File is empty.")

    def _build_blocks(
        self, document_id: str, part: UploadedPart, job: MedReconciliationJob
    ) -> list[SourceBlock]:
        if self._document_ai.is_configured:
            try:
                blocks = self._document_ai.process_to_blocks(
                    document_id, part.data, part.content_type
                )
                if blocks:
                    return blocks
                job.validation_findings.append(
                    ValidationFinding(
                        code="DOCUMENT_AI_PROCESSOR_MISMATCH",
                        message=f"Document AI returned no blocks for {part.filename}.",
                        requires_review=True,
                    )
                )
            except DocumentAIConfigurationError:
                raise
            except Exception:
                logger.exception("Document AI processing failed")
                job.validation_findings.append(
                    ValidationFinding(
                        code="DOCUMENT_AI_PROCESSOR_MISMATCH",
                        message=f"Document AI failed for {part.filename}.",
                        requires_review=True,
                    )
                )

        pages = extract_text_pages(part.data, part.content_type)
        vertex_blocks: list[SourceBlock] = []
        for page_num, text in pages:
            if not text.strip():
                continue
            vertex_blocks.append(
                SourceBlock(
                    source_block_id=f"{document_id}:p{page_num}:b1",
                    document_id=document_id,
                    page_number=page_num,
                    text=text,
                    evidence_status=EvidenceStatus.VERTEX_ONLY,
                )
            )
        if not vertex_blocks:
            vertex_blocks.append(
                SourceBlock(
                    source_block_id=f"{document_id}:p1:b1",
                    document_id=document_id,
                    page_number=1,
                    text="",
                    evidence_status=EvidenceStatus.VERTEX_ONLY,
                )
            )
        job.reconciliation_used_weak_evidence = True
        return vertex_blocks


def _medications_from_vertex(
    document_id: str,
    catalog: SourceBlockCatalog,
    vertex_out: object,
    fields: list[ExtractedField],
) -> list[MedicationLine]:
    from app.schemas.meddocs import VertexExtractOutput

    if not isinstance(vertex_out, VertexExtractOutput):
        return []
    lines: list[MedicationLine] = []
    for med in vertex_out.medications:
        name = med.get("medication_name")
        if not name:
            continue
        block_ids = list(med.get("source_block_ids") or [])
        block = None
        for bid in block_ids:
            block = catalog.get_block(document_id, bid)
            if block:
                break
        if not block:
            continue
        ref = SourceRef(
            document_id=document_id,
            page_number=block.page_number,
            source_text=block.text[:120],
            text_anchor=block.source_block_id,
            bounding_box=block.bounding_box,
            extraction_method="vertex_structured",
            confidence=block.confidence,
            evidence_status=block.evidence_status,
        )
        lines.append(
            MedicationLine(
                medication_name=normalize_medication_name(str(name)),
                strength=med.get("strength"),
                dose=med.get("dose"),
                route=med.get("route"),
                frequency=med.get("frequency"),
                source_ref=ref,
                evidence_status=block.evidence_status,
            )
        )
    return lines
