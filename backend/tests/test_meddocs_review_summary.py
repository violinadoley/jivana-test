from app.core.config import Settings
from app.core.deps import get_document_store
from app.main import app
from app.schemas.meddocs import CaseStatus, JobStatus, MedReconciliationJob
from app.services.documents.document_store import DocumentStore
from fastapi.testclient import TestClient


def test_review_summary_html(client: TestClient) -> None:
    store = DocumentStore(Settings(FIREBASE_PROJECT_ID=None))
    job = MedReconciliationJob(
        job_id="summary-case",
        status=JobStatus.NEEDS_REVIEW,
        case_status=CaseStatus.AWAITING_REVIEW,
        case_label="Demo summary",
        synthetic_mrn="SYN-1",
    )
    store.save_job(job)
    app.dependency_overrides[get_document_store] = lambda: store
    try:
        response = client.get("/api/v1/meddocs/cases/summary-case/review-summary")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        assert "Demo summary" in response.text
        assert "Synthetic demo" in response.text
    finally:
        app.dependency_overrides.pop(get_document_store, None)
