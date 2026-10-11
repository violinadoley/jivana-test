import uuid
from datetime import UTC, datetime
from typing import Any

from app.core.exceptions import AppException
from app.schemas.meddocs import (
    CLOSURE_ITEM_STATUSES,
    CaseAttestation,
    CaseFinalizationRecord,
    CaseStatus,
    DiscrepancyItem,
    DiscrepancyItemStatus,
    ItemReviewEvent,
    ItemReviewPatchRequest,
    MedReconciliationJob,
)
from app.services.documents.case_status import can_finalize, sync_legacy_job_status
from app.services.documents.discrepancy_items import all_items_in_closure
from app.services.documents.item_review_transitions import validate_item_review_request
from app.services.documents.module2_export import on_reconciliation_completed


def reviewer_from_user(user: dict[str, Any] | None) -> tuple[str | None, str]:
    if not user:
        return None, "anonymous-demo"
    uid = str(user.get("uid")) if user.get("uid") else None
    display = str(user.get("email") or user.get("name") or uid or "anonymous-demo")[:120]
    return uid, display


_SUPPORTED_TRANSITIONS = frozenset({"discharge", "admission", "transfer"})


def assert_supported_transition(transition_type: str) -> None:
    if transition_type not in _SUPPORTED_TRANSITIONS:
        raise AppException(
            "UNSUPPORTED_TRANSITION",
            "transition_type must be discharge, admission, or transfer.",
            status_code=422,
        )


def assert_discharge_transition(transition_type: str) -> None:
    """Backward-compatible alias."""
    assert_supported_transition(transition_type)


def begin_item_review(
    job: MedReconciliationJob,
    user: dict[str, Any] | None,
) -> MedReconciliationJob:
    if job.case_status != CaseStatus.LEGACY_BULK_ACKNOWLEDGED:
        raise AppException(
            "INVALID_STATE",
            "Begin item review is only for legacy bulk acknowledged cases.",
            status_code=409,
        )
    uid, display = reviewer_from_user(user)
    now = datetime.now(UTC).isoformat()
    job.legacy_item_review_started = True
    job.review_granularity = "per_item"
    job.item_review_phase = "in_progress"
    for item in job.discrepancy_items:
        if item.status == DiscrepancyItemStatus.LEGACY_UNREVIEWED:
            event = ItemReviewEvent(
                event_id=uuid.uuid4().hex,
                from_status=DiscrepancyItemStatus.LEGACY_UNREVIEWED,
                to_status=DiscrepancyItemStatus.OPEN,
                reviewed_at=now,
                reviewer_uid=uid,
                reviewer_display=display,
                note="Legacy item review started.",
            )
            _append_event(item, event)
            item.status = DiscrepancyItemStatus.OPEN
    sync_legacy_job_status(job)
    return job


def patch_item(
    job: MedReconciliationJob,
    item_id: str,
    body: ItemReviewPatchRequest,
    user: dict[str, Any] | None,
) -> MedReconciliationJob:
    reopen_only = body.to_status == DiscrepancyItemStatus.OPEN
    if job.case_status == CaseStatus.REVIEW_DOCUMENTED and not reopen_only:
        raise AppException(
            "INVALID_STATE",
            "Reopen items on a documented case before other changes.",
            status_code=409,
        )

    item = _find_item(job, item_id)
    from_status = item.status

    validate_item_review_request(job, item, body)
    uid, display = reviewer_from_user(user)
    now = datetime.now(UTC).isoformat()

    to_status = body.to_status
    if from_status in CLOSURE_ITEM_STATUSES and to_status == DiscrepancyItemStatus.OPEN:
        to_status = DiscrepancyItemStatus.OPEN

    event = ItemReviewEvent(
        event_id=uuid.uuid4().hex,
        from_status=from_status,
        to_status=to_status,
        reviewed_at=now,
        reviewer_uid=uid,
        reviewer_display=display,
        note=body.note.strip(),
        clarification_note=_strip(body.clarification_note),
        external_action_required=_strip(body.external_action_required),
        external_evidence=_strip(body.external_evidence),
        verification_basis=_strip(body.verification_basis),
        dismissal_rationale=_strip(body.dismissal_rationale),
        reopen_reason=_strip(body.reopen_reason),
    )
    _append_event(item, event)
    item.status = to_status

    if job.case_status == CaseStatus.REVIEW_DOCUMENTED and to_status == DiscrepancyItemStatus.OPEN:
        _supersede_finalization(job, reason=body.reopen_reason or body.note)

    if job.case_status == CaseStatus.LEGACY_BULK_ACKNOWLEDGED and job.legacy_item_review_started:
        job.case_status = CaseStatus.LEGACY_BULK_ACKNOWLEDGED

    job.item_review_phase = "in_progress"
    sync_legacy_job_status(job)
    return job


def complete_item_review(job: MedReconciliationJob) -> MedReconciliationJob:
    if job.case_status not in (
        CaseStatus.AWAITING_REVIEW,
        CaseStatus.LEGACY_BULK_ACKNOWLEDGED,
    ):
        raise AppException(
            "INVALID_STATE",
            "Case is not eligible for complete-item-review.",
            status_code=409,
        )
    if not all_items_in_closure(job):
        raise AppException(
            "INVALID_STATE",
            "All items must be in closure states before completing item review.",
            status_code=422,
        )
    job.case_status = CaseStatus.AWAITING_REVIEW
    job.item_review_phase = "complete"
    sync_legacy_job_status(job)
    return job


def finalize_case(
    job: MedReconciliationJob,
    user: dict[str, Any] | None,
    *,
    attestation_note: str | None,
    weak_evidence_acknowledged: bool,
    no_discrepancies_attestation: bool,
) -> MedReconciliationJob:
    if job.case_status == CaseStatus.LEGACY_BULK_ACKNOWLEDGED:
        raise AppException(
            "INVALID_STATE",
            "Complete item review and move to awaiting_review before finalize.",
            status_code=409,
        )

    uid, display = reviewer_from_user(user)
    now = datetime.now(UTC).isoformat()

    if not job.discrepancy_items and no_discrepancies_attestation:
        job.attestation = CaseAttestation(
            attested_at=now,
            attested_by_uid=uid,
            attested_by_display=display,
            no_discrepancies=True,
            weak_evidence_acknowledged=weak_evidence_acknowledged,
            note=attestation_note,
        )

    if job.reconciliation_used_weak_evidence and weak_evidence_acknowledged:
        job.attestation = job.attestation or CaseAttestation(
            attested_at=now,
            attested_by_uid=uid,
            attested_by_display=display,
        )
        job.attestation.weak_evidence_acknowledged = True
        if attestation_note:
            job.attestation.note = attestation_note

    ok, msg = can_finalize(job)
    if not ok:
        raise AppException("INVALID_STATE", msg or "Cannot finalize.", status_code=422)

    job.case_status = CaseStatus.REVIEW_DOCUMENTED
    job.finalized_at = now
    job.finalized_by_uid = uid
    job.finalized_by_display = display
    job.finalization_history.append(
        CaseFinalizationRecord(
            finalized_at=now,
            finalized_by_uid=uid,
            finalized_by_display=display,
        )
    )
    sync_legacy_job_status(job)
    job = on_reconciliation_completed(job)
    if job.finalization_history:
        job.finalization_history[-1].fhir_export_resource = job.fhir_export_resource
    return job


def _supersede_finalization(job: MedReconciliationJob, reason: str) -> None:
    now = datetime.now(UTC).isoformat()
    for record in reversed(job.finalization_history):
        if not record.superseded_at:
            record.superseded_at = now
            record.superseded_reason = reason[:500]
            break
    job.case_status = CaseStatus.AWAITING_REVIEW
    job.item_review_phase = "in_progress"
    job.finalized_at = None
    job.finalized_by_uid = None
    job.finalized_by_display = None


def _find_item(job: MedReconciliationJob, item_id: str) -> DiscrepancyItem:
    for item in job.discrepancy_items:
        if item.item_id == item_id:
            return item
    raise AppException("NOT_FOUND", "Discrepancy item not found.", status_code=404)


def _append_event(item: DiscrepancyItem, event: ItemReviewEvent) -> None:
    item.review_history.append(event)
    item.review = event


def _strip(value: str | None) -> str | None:
    if value is None:
        return None
    s = value.strip()
    return s if s else None
