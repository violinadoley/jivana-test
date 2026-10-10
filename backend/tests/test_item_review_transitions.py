import pytest
from app.core.exceptions import AppException
from app.schemas.meddocs import (
    DiscrepancyItem,
    DiscrepancyItemStatus,
    DiscrepancyType,
    ItemReviewPatchRequest,
    JobStatus,
    MedDiscrepancy,
    MedReconciliationJob,
)
from app.services.documents.item_review_transitions import (
    validate_item_review_request,
    validate_item_transition,
)


def test_awaiting_external_to_intentional_rejected() -> None:
    body = ItemReviewPatchRequest(
        to_status=DiscrepancyItemStatus.RESOLVED_INTENTIONAL,
        note="x" * 15,
        verification_basis="y" * 15,
    )
    with pytest.raises(AppException) as exc:
        validate_item_transition(DiscrepancyItemStatus.AWAITING_EXTERNAL_ACTION, body)
    assert exc.value.code == "INVALID_ITEM_TRANSITION"


def test_reopen_requires_reason() -> None:
    body = ItemReviewPatchRequest(
        to_status=DiscrepancyItemStatus.OPEN,
        note="short",
        reopen_reason="also short",
    )
    with pytest.raises(AppException):
        validate_item_transition(DiscrepancyItemStatus.RESOLVED_INTENTIONAL, body)


def test_legacy_bulk_gate_rejects_patch_before_begin() -> None:
    item = DiscrepancyItem(
        item_id="i1",
        discrepancy=MedDiscrepancy(
            discrepancy_type=DiscrepancyType.DOSE_MISMATCH,
            summary="test",
        ),
        status=DiscrepancyItemStatus.LEGACY_UNREVIEWED,
    )
    job = MedReconciliationJob(
        job_id="c1",
        status=JobStatus.NEEDS_REVIEW,
        review_granularity="legacy_bulk",
        legacy_item_review_started=False,
        discrepancy_items=[item],
    )
    body = ItemReviewPatchRequest(
        to_status=DiscrepancyItemStatus.RESOLVED_NOT_RELEVANT,
        note="n" * 20,
        dismissal_rationale="d" * 20,
    )
    with pytest.raises(AppException) as exc:
        validate_item_review_request(job, item, body)
    assert exc.value.code == "LEGACY_REVIEW_NOT_STARTED"


def test_intentional_requires_verification_basis() -> None:
    body = ItemReviewPatchRequest(
        to_status=DiscrepancyItemStatus.RESOLVED_INTENTIONAL,
        note="n" * 20,
        verification_basis="v" * 10,
    )
    with pytest.raises(AppException):
        validate_item_transition(DiscrepancyItemStatus.OPEN, body)
