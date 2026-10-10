from app.core.config import Settings
from app.core.deps import get_document_store
from app.main import app
from app.schemas.meddocs import CaseStatus, JobStatus, MedReconciliationJob
from app.services.documents.document_store import DocumentStore
from fastapi.testclient import TestClient


def test_list_cases_filter(client: TestClient) -> None:
    settings = Settings()
    store = DocumentStore(settings, firestore=None)
    store.save_job(
        MedReconciliationJob(
            job_id="d1",
            status=JobStatus.NEEDS_REVIEW,
            case_status=CaseStatus.DRAFT,
            case_label="Draft case",
        )
    )
    store.save_job(
        MedReconciliationJob(
            job_id="l1",
            status=JobStatus.NEEDS_REVIEW,
            case_status=CaseStatus.LEGACY_BULK_ACKNOWLEDGED,
            case_label="Legacy",
        )
    )
    app.dependency_overrides[get_document_store] = lambda: store
    try:
        draft = client.get("/api/v1/meddocs/cases", params={"status": "draft"})
        assert draft.status_code == 200
        assert len(draft.json()) == 1
        legacy = client.get("/api/v1/meddocs/cases", params={"status": "legacy_bulk_acknowledged"})
        assert len(legacy.json()) == 1
    finally:
        app.dependency_overrides.pop(get_document_store, None)
