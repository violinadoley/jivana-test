from dataclasses import dataclass

from app.core.exceptions import AppException
from app.schemas.meddocs import (
    CLOSURE_ITEM_STATUSES,
    DiscrepancyItem,
    DiscrepancyItemStatus,
    ItemReviewPatchRequest,
    MedReconciliationJob,
)


@dataclass(frozen=True)
class TransitionSpec:
    min_note: int
    required_fields: tuple[str, ...]


_TRANSITIONS: dict[tuple[DiscrepancyItemStatus, DiscrepancyItemStatus], TransitionSpec] = {
    (DiscrepancyItemStatus.OPEN, DiscrepancyItemStatus.PENDING_CLARIFICATION): TransitionSpec(
        10, ("clarification_note",)
    ),
    (DiscrepancyItemStatus.LEGACY_UNREVIEWED, DiscrepancyItemStatus.PENDING_CLARIFICATION): (
        TransitionSpec(10, ("clarification_note",))
    ),
    (DiscrepancyItemStatus.OPEN, DiscrepancyItemStatus.AWAITING_EXTERNAL_ACTION): TransitionSpec(
        15, ("external_action_required",)
    ),
    (DiscrepancyItemStatus.LEGACY_UNREVIEWED, DiscrepancyItemStatus.AWAITING_EXTERNAL_ACTION): (
        TransitionSpec(15, ("external_action_required",))
    ),
    (DiscrepancyItemStatus.PENDING_CLARIFICATION, DiscrepancyItemStatus.AWAITING_EXTERNAL_ACTION): (
        TransitionSpec(15, ("external_action_required",))
    ),
    (DiscrepancyItemStatus.OPEN, DiscrepancyItemStatus.RESOLVED_INTENTIONAL): TransitionSpec(
        15, ("verification_basis",)
    ),
    (DiscrepancyItemStatus.LEGACY_UNREVIEWED, DiscrepancyItemStatus.RESOLVED_INTENTIONAL): (
        TransitionSpec(15, ("verification_basis",))
    ),
    (DiscrepancyItemStatus.PENDING_CLARIFICATION, DiscrepancyItemStatus.RESOLVED_INTENTIONAL): (
        TransitionSpec(15, ("verification_basis",))
    ),
    (DiscrepancyItemStatus.OPEN, DiscrepancyItemStatus.RESOLVED_NOT_RELEVANT): TransitionSpec(
        20, ("dismissal_rationale",)
    ),
    (DiscrepancyItemStatus.LEGACY_UNREVIEWED, DiscrepancyItemStatus.RESOLVED_NOT_RELEVANT): (
        TransitionSpec(20, ("dismissal_rationale",))
    ),
    (DiscrepancyItemStatus.PENDING_CLARIFICATION, DiscrepancyItemStatus.RESOLVED_NOT_RELEVANT): (
        TransitionSpec(20, ("dismissal_rationale",))
    ),
    (
        DiscrepancyItemStatus.AWAITING_EXTERNAL_ACTION,
        DiscrepancyItemStatus.RESOLVED_EXTERNALLY_CLOSED,
    ): TransitionSpec(15, ("external_evidence",)),
    (
        DiscrepancyItemStatus.AWAITING_EXTERNAL_ACTION,
        DiscrepancyItemStatus.RESOLVED_NOT_RELEVANT,
    ): TransitionSpec(20, ("dismissal_rationale",)),
}

_REOPEN_FROM = CLOSURE_ITEM_STATUSES


def validate_item_review_request(
    job: MedReconciliationJob,
    item: DiscrepancyItem,
    body: ItemReviewPatchRequest,
) -> None:
    """Case-aware gate: legacy bulk cases require begin-item-review before any item PATCH."""
    if job.review_granularity == "legacy_bulk":
        raise AppException(
            "LEGACY_REVIEW_NOT_STARTED",
            "Call begin-item-review before resolving legacy items.",
            status_code=422,
        )
    validate_item_transition(item.status, body)


def validate_item_transition(
    from_status: DiscrepancyItemStatus,
    body: ItemReviewPatchRequest,
) -> None:
    to_status = body.to_status

    if to_status == DiscrepancyItemStatus.OPEN and from_status in _REOPEN_FROM:
        _check_min(body.reopen_reason, 15, "reopen_reason")
        _check_min(body.note, 10, "note")
        return

    key = (from_status, to_status)
    spec = _TRANSITIONS.get(key)
    if spec is None:
        raise AppException(
            "INVALID_ITEM_TRANSITION",
            f"Transition {from_status.value} → {to_status.value} is not allowed.",
            status_code=422,
        )

    _check_min(body.note, spec.min_note, "note")
    for field in spec.required_fields:
        value = getattr(body, field, None)
        _check_min(value, spec.min_note, field)

    if from_status == DiscrepancyItemStatus.AWAITING_EXTERNAL_ACTION and to_status in (
        DiscrepancyItemStatus.RESOLVED_INTENTIONAL,
    ):
        raise AppException(
            "INVALID_ITEM_TRANSITION",
            "Close external actions via resolved_externally_closed or dismiss.",
            status_code=422,
        )

    if to_status == DiscrepancyItemStatus.RESOLVED_EXTERNALLY_CLOSED and from_status != (
        DiscrepancyItemStatus.AWAITING_EXTERNAL_ACTION
    ):
        raise AppException(
            "INVALID_ITEM_TRANSITION",
            "resolved_externally_closed requires awaiting_external_action first.",
            status_code=422,
        )


def _check_min(value: str | None, minimum: int, field: str) -> None:
    if not value or len(value.strip()) < minimum:
        raise AppException(
            "INVALID_ITEM_TRANSITION",
            f"Field '{field}' must be at least {minimum} characters.",
            status_code=422,
        )
