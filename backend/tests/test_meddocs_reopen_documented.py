import pytest
from app.core.exceptions import AppException
from app.schemas.meddocs import (
    CaseFinalizationRecord,
    CaseStatus,
    DiscrepancyItem,
    DiscrepancyItemStatus,
    DiscrepancyType,
    ItemReviewPatchRequest,
    JobStatus,
    MedDiscrepancy,
    MedReconciliationJob,
)
from app.services.documents.case_workflow import finalize_case, patch_item
from app.services.documents.review_summary import render_review_summary_html


def _documented_job() -> MedReconciliationJob:
    item = DiscrepancyItem(
        item_id="i1",
        discrepancy=MedDiscrepancy(
            discrepancy_type=DiscrepancyType.DOSE_MISMATCH,
            summary="test",
        ),
        status=DiscrepancyItemStatus.RESOLVED_INTENTIONAL,
        review_history=[],
    )
    return MedReconciliationJob(
        job_id="c1",
        status=JobStatus.COMPLETED,
        case_status=CaseStatus.REVIEW_DOCUMENTED,
        finalized_at="2020-01-01T00:00:00+00:00",
        finalized_by_display="Reviewer One",
        finalization_history=[
            CaseFinalizationRecord(
                finalized_at="2020-01-01T00:00:00+00:00",
                finalized_by_display="Reviewer One",
            )
        ],
        discrepancy_items=[item],
    )


def test_reopen_on_documented_case_returns_to_awaiting_review() -> None:
    job = _documented_job()
    item_hist_len = len(job.discrepancy_items[0].review_history)
    fin_hist_len = len(job.finalization_history)
    body = ItemReviewPatchRequest(
        to_status=DiscrepancyItemStatus.OPEN,
        note="Reopening documented case for audit.",
        reopen_reason="Additional source document received offline.",
    )
    job = patch_item(job, "i1", body, {"uid": "u1"})
    assert job.case_status == CaseStatus.AWAITING_REVIEW
    assert job.finalization_history[0].superseded_at is not None
    assert job.finalized_at is None
    assert len(job.discrepancy_items[0].review_history) == item_hist_len + 1
    assert len(job.finalization_history) == fin_hist_len


def test_finalize_blocked_after_reopen_until_closure() -> None:
    job = _documented_job()
    body = ItemReviewPatchRequest(
        to_status=DiscrepancyItemStatus.OPEN,
        note="Reopening documented case for audit.",
        reopen_reason="Additional source document received offline.",
    )
    job = patch_item(job, "i1", body, {"uid": "u1"})
    with pytest.raises(AppException):
        finalize_case(
            job,
            {"uid": "u1"},
            attestation_note=None,
            weak_evidence_acknowledged=False,
            no_discrepancies_attestation=False,
        )


def test_re_finalize_appends_finalization_history() -> None:
    job = _documented_job()
    reopen = ItemReviewPatchRequest(
        to_status=DiscrepancyItemStatus.OPEN,
        note="Reopening documented case for audit.",
        reopen_reason="Additional source document received offline.",
    )
    job = patch_item(job, "i1", reopen, {"uid": "u1"})
    resolve = ItemReviewPatchRequest(
        to_status=DiscrepancyItemStatus.RESOLVED_NOT_RELEVANT,
        note="n" * 20,
        dismissal_rationale="d" * 20,
    )
    job = patch_item(job, "i1", resolve, {"uid": "u1"})
    job = finalize_case(
        job,
        {"uid": "u2", "email": "reviewer2@example.com"},
        attestation_note="Second attestation.",
        weak_evidence_acknowledged=False,
        no_discrepancies_attestation=False,
    )
    assert job.case_status == CaseStatus.REVIEW_DOCUMENTED
    assert len(job.finalization_history) == 2
    assert job.finalization_history[0].superseded_at is not None
    assert job.finalization_history[1].superseded_at is None


def test_review_summary_lists_superseded_finalizations() -> None:
    job = _documented_job()
    reopen = ItemReviewPatchRequest(
        to_status=DiscrepancyItemStatus.OPEN,
        note="Reopening documented case for audit.",
        reopen_reason="Additional source document received offline.",
    )
    job = patch_item(job, "i1", reopen, {"uid": "u1"})
    html = render_review_summary_html(job)
    assert "Prior finalizations (superseded)" in html
    assert "Reviewer One" in html
