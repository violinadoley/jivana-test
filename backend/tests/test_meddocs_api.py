import io

from app.core.deps import get_document_store, get_meddocs_pipeline
from app.main import app
from app.schemas.meddocs import JobStatus
from fastapi.testclient import TestClient

from meddocs_helpers import FakeDocumentAIClient, FakeVertexMeddocsClient
from test_meddocs_pipeline import _pipeline


def test_meddocs_reconciliation_endpoint(client: TestClient) -> None:
    stub = _pipeline(
        docai=FakeDocumentAIClient(), vertex=FakeVertexMeddocsClient(), processor_id="p"
    )
    store = stub._store  # noqa: SLF001 — test wiring
    app.dependency_overrides[get_meddocs_pipeline] = lambda: stub
    app.dependency_overrides[get_document_store] = lambda: store
    try:
        files = [
            ("files", ("prior_meds.txt", io.BytesIO(b"MRN 1\nPrior\nMed"), "text/plain")),
            (
                "files",
                ("discharge_summary.txt", io.BytesIO(b"MRN 1\nDischarge\nMed"), "text/plain"),
            ),
            ("files", ("current_rx.txt", io.BytesIO(b"MRN 1\nRx\nMed"), "text/plain")),
        ]
        resp = client.post("/api/v1/meddocs/reconciliation", files=files)
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] in (JobStatus.COMPLETED.value, JobStatus.NEEDS_REVIEW.value)
        job_id = body["job_id"]
        get_resp = client.get(f"/api/v1/meddocs/reconciliation/{job_id}")
        assert get_resp.status_code == 200
    finally:
        app.dependency_overrides.pop(get_meddocs_pipeline, None)
