import io

from app.core.deps import get_document_store, get_meddocs_pipeline
from app.main import app
from app.schemas.meddocs import CaseStatus, DiscrepancyItemStatus
from app.services.documents.intake_pipeline import UploadedPart
from fastapi.testclient import TestClient

from meddocs_helpers import FakeDocumentAIClient, FakeVertexMeddocsClient
from test_meddocs_pipeline import _pipeline


def _mismatch_bundle() -> list[UploadedPart]:
    """Three-way bundle that yields at least one reconciliation discrepancy."""
    return [
        UploadedPart(
            "prior_meds.txt",
            "text/plain",
            b"MRN 12345\nPrior\nLisinopril 10 mg daily",
        ),
        UploadedPart(
            "discharge_summary.txt",
            "text/plain",
            b"MRN 12345\nDocumented change to 20 mg\nDischarge\nLisinopril 20 mg daily",
        ),
        UploadedPart(
            "current_rx.txt",
            "text/plain",
            b"MRN 12345\nRx\nLisinopril 10 mg daily",
        ),
    ]


def test_legacy_bulk_blocks_finalize_until_item_review(client: TestClient) -> None:
    vertex = FakeVertexMeddocsClient(discharge_dose="20 mg")
    stub = _pipeline(
        docai=FakeDocumentAIClient(),
        vertex=vertex,
        processor_id="p",
    )
    store = stub._store  # noqa: SLF001
    app.dependency_overrides[get_meddocs_pipeline] = lambda: stub
    app.dependency_overrides[get_document_store] = lambda: store
    try:
        bundle = _mismatch_bundle()
        files = [("files", (p.filename, io.BytesIO(p.data), p.content_type)) for p in bundle]
        resp = client.post("/api/v1/meddocs/reconciliation", files=files)
        job_id = resp.json()["job_id"]
        legacy = client.post(
            f"/api/v1/meddocs/reconciliation/{job_id}/review-legacy",
            json={"note": "Bulk ack for migration test"},
        )
        assert legacy.status_code == 200

        job = store.get_job(job_id)
        assert job.case_status == CaseStatus.LEGACY_BULK_ACKNOWLEDGED
        assert job.discrepancy_items
        assert job.discrepancy_items[0].status == DiscrepancyItemStatus.LEGACY_UNREVIEWED

        fin = client.post(f"/api/v1/meddocs/cases/{job_id}/finalize-review", json={})
        assert fin.status_code == 409

        patch = client.patch(
            f"/api/v1/meddocs/cases/{job_id}/items/{job.discrepancy_items[0].item_id}",
            json={
                "to_status": "resolved_not_relevant",
                "note": "Dismiss after manual check of sources.",
                "dismissal_rationale": "Algorithm flagged duplicate line formatting only.",
            },
        )
        assert patch.status_code == 422

        begin = client.post(f"/api/v1/meddocs/cases/{job_id}/begin-item-review")
        assert begin.status_code == 200

        patch2 = client.patch(
            f"/api/v1/meddocs/cases/{job_id}/items/{job.discrepancy_items[0].item_id}",
            json={
                "to_status": "resolved_not_relevant",
                "note": "Dismiss after manual check of sources.",
                "dismissal_rationale": "Algorithm flagged duplicate line formatting only.",
            },
        )
        assert patch2.status_code == 200

        for item in store.get_job(job_id).discrepancy_items[1:]:
            client.patch(
                f"/api/v1/meddocs/cases/{job_id}/items/{item.item_id}",
                json={
                    "to_status": "resolved_not_relevant",
                    "note": "Dismiss after manual check of sources.",
                    "dismissal_rationale": "Algorithm flagged duplicate line formatting only.",
                },
            )

        complete = client.post(f"/api/v1/meddocs/cases/{job_id}/complete-item-review")
        assert complete.status_code == 200
        assert store.get_job(job_id).case_status == CaseStatus.AWAITING_REVIEW

        fin2 = client.post(
            f"/api/v1/meddocs/cases/{job_id}/finalize-review",
            json={"weak_evidence_acknowledged": True},
        )
        assert fin2.status_code == 200
        assert store.get_job(job_id).case_status == CaseStatus.REVIEW_DOCUMENTED
    finally:
        app.dependency_overrides.pop(get_meddocs_pipeline, None)
        app.dependency_overrides.pop(get_document_store, None)
