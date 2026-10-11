import uuid

from app.schemas.meddocs import (
    DiscrepancyItem,
    DiscrepancyItemStatus,
    MedReconciliationJob,
)


def materialize_discrepancy_items(
    job: MedReconciliationJob,
    *,
    initial_status: DiscrepancyItemStatus = DiscrepancyItemStatus.OPEN,
) -> list[DiscrepancyItem]:
    items: list[DiscrepancyItem] = []
    for disc in job.discrepancies:
        items.append(
            DiscrepancyItem(
                item_id=uuid.uuid4().hex,
                kind="medication_discrepancy",
                discrepancy=disc,
                status=initial_status,
                review_history=[],
            )
        )
    for finding in job.validation_findings:
        if not finding.requires_review:
            continue
        items.append(
            DiscrepancyItem(
                item_id=uuid.uuid4().hex,
                kind="validation_finding",
                finding=finding,
                status=initial_status,
                review_history=[],
            )
        )
    return items


def all_items_in_closure(job: MedReconciliationJob) -> bool:
    if not job.discrepancy_items:
        return True
    from app.schemas.meddocs import CLOSURE_ITEM_STATUSES

    return all(item.status in CLOSURE_ITEM_STATUSES for item in job.discrepancy_items)


def has_non_closure_items(job: MedReconciliationJob) -> bool:
    from app.schemas.meddocs import NON_CLOSURE_ITEM_STATUSES

    return any(item.status in NON_CLOSURE_ITEM_STATUSES for item in job.discrepancy_items)
