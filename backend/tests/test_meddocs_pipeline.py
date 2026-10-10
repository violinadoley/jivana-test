from app.core.config import Settings
from app.schemas.meddocs import EvidenceStatus, JobStatus
from app.services.documents.document_ai_service import DocumentAIService
from app.services.documents.document_store import DocumentStore
from app.services.documents.intake_pipeline import MeddocsIntakePipeline, UploadedPart
from app.services.documents.vertex_gemini_service import VertexGeminiMeddocsService
from app.services.storage.storage_service import StorageService

from meddocs_helpers import FakeDocumentAIClient, FakeVertexMeddocsClient


def _pipeline(
    *,
    docai: FakeDocumentAIClient | None = None,
    vertex: FakeVertexMeddocsClient | None = None,
    processor_id: str = "",
) -> MeddocsIntakePipeline:
    settings = Settings(
        DOCUMENT_AI_PROCESSOR_ID=processor_id or None,
        GCP_PROJECT_ID="test-gcp",
        FIREBASE_PROJECT_ID=None,
    )
    storage = StorageService(settings)
    store = DocumentStore(settings, firestore=None)
    dai = DocumentAIService(settings, client=docai)
    vtx = VertexGeminiMeddocsService(settings, client=vertex)
    return MeddocsIntakePipeline(settings, storage, store, dai, vtx)


def _bundle() -> list[UploadedPart]:
    prior = b"MRN 12345\nPrior record\nLisinopril 10 mg daily"
    discharge = b"MRN 12345\nDischarge summary\nLisinopril 10 mg daily"
    rx = b"MRN 12345\nCurrent prescription\nLisinopril 10 mg daily"
    return [
        UploadedPart("prior_meds.txt", "text/plain", prior),
        UploadedPart("discharge_summary.txt", "text/plain", discharge),
        UploadedPart("current_rx.txt", "text/plain", rx),
    ]


def test_completed_requires_verified_evidence_on_compared_fields() -> None:
    docai = FakeDocumentAIClient()
    vertex = FakeVertexMeddocsClient()
    job = _pipeline(docai=docai, vertex=vertex, processor_id="proc").run_reconciliation(
        _bundle(), owner_uid=None
    )
    assert job.status == JobStatus.COMPLETED
    assert job.reconciliation_used_weak_evidence is False
    assert job.discrepancies == []


def test_vertex_only_evidence_forces_needs_review_despite_matching_meds() -> None:
    vertex = FakeVertexMeddocsClient()
    job = _pipeline(vertex=vertex).run_reconciliation(_bundle(), owner_uid=None)
    assert job.status == JobStatus.NEEDS_REVIEW
    assert job.reconciliation_used_weak_evidence is True
    for meds in job.medications_by_document.values():
        for med in meds:
            assert med.evidence_status == EvidenceStatus.VERTEX_ONLY


def test_no_auto_complete_when_any_discrepancy() -> None:
    vertex = FakeVertexMeddocsClient(discharge_dose="20 mg")
    docai = FakeDocumentAIClient()
    discharge = b"MRN 12345\nDocumented change to 20 mg\nDischarge\nLisinopril 20 mg daily"
    files = [
        UploadedPart(
            "prior_meds.txt",
            "text/plain",
            b"MRN 12345\nPrior\nLisinopril 10 mg daily",
        ),
        UploadedPart("discharge_summary.txt", "text/plain", discharge),
        UploadedPart(
            "current_rx.txt",
            "text/plain",
            b"MRN 12345\nRx\nLisinopril 10 mg daily",
        ),
    ]
    job = _pipeline(docai=docai, vertex=vertex, processor_id="proc").run_reconciliation(
        files, owner_uid=None
    )
    assert job.discrepancies
    assert job.status == JobStatus.NEEDS_REVIEW


def test_docai_unset_conservative_review_routing() -> None:
    job = _pipeline(vertex=FakeVertexMeddocsClient()).run_reconciliation(_bundle(), owner_uid=None)
    assert job.status == JobStatus.NEEDS_REVIEW


def test_docai_invalid_processor_fails_job() -> None:
    docai = FakeDocumentAIClient(fail_verify=True)
    pipeline = _pipeline(docai=docai, processor_id="bad")
    try:
        pipeline.run_reconciliation(_bundle(), owner_uid=None)
        raise AssertionError("expected failure")
    except Exception as exc:
        from app.core.exceptions import DocumentAIConfigurationError

        assert isinstance(exc, DocumentAIConfigurationError)
