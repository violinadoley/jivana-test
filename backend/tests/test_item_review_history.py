from app.schemas.meddocs import (
    CaseStatus,
    DiscrepancyItem,
    DiscrepancyItemStatus,
    DiscrepancyType,
    ItemReviewPatchRequest,
    JobStatus,
    MedDiscrepancy,
    MedReconciliationJob,
)
from app.services.documents.case_workflow import patch_item


def _job_with_item() -> MedReconciliationJob:
    item = DiscrepancyItem(
        item_id="item1",
        discrepancy=MedDiscrepancy(
            discrepancy_type=DiscrepancyType.DOSE_MISMATCH,
            summary="Dose differs",
        ),
        status=DiscrepancyItemStatus.OPEN,
    )
    return MedReconciliationJob(
        job_id="c1",
        status=JobStatus.NEEDS_REVIEW,
        case_status=CaseStatus.AWAITING_REVIEW,
        discrepancy_items=[item],
    )


def test_patch_appends_history() -> None:
    job = _job_with_item()
    body = ItemReviewPatchRequest(
        to_status=DiscrepancyItemStatus.RESOLVED_INTENTIONAL,
        note="Verified against discharge summary text.",
        verification_basis="Discharge summary page 1 cites dose change.",
    )
    job = patch_item(job, "item1", body, {"uid": "u1", "email": "pharm@test.com"})
    item = job.discrepancy_items[0]
    assert len(item.review_history) == 1
    assert item.review_history[0].reviewer_uid == "u1"
    assert item.review is item.review_history[0]


def test_reopen_preserves_history() -> None:
    job = _job_with_item()
    resolve = ItemReviewPatchRequest(
        to_status=DiscrepancyItemStatus.RESOLVED_NOT_RELEVANT,
        note="Not applicable to this transition.",
        dismissal_rationale="Duplicate entry across sources only.",
    )
    job = patch_item(job, "item1", resolve, {"uid": "u1"})
    reopen = ItemReviewPatchRequest(
        to_status=DiscrepancyItemStatus.OPEN,
        note="Reopening after new document upload.",
        reopen_reason="New Rx document uploaded for comparison.",
    )
    job = patch_item(job, "item1", reopen, {"uid": "u2"})
    item = job.discrepancy_items[0]
    assert len(item.review_history) == 2
    assert item.status == DiscrepancyItemStatus.OPEN
