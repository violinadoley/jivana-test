from app.schemas.meddocs import (
    NON_CLOSURE_ITEM_STATUSES,
    CaseStatus,
    DiscrepancyItemStatus,
)
from app.services.documents.document_store import DocumentStore


def compute_medrec_metrics(store: DocumentStore, owner_uid: str | None) -> dict[str, int]:
    cases = store.list_cases(owner_uid, limit=200)
    awaiting = 0
    legacy = 0
    documented = 0
    open_items = 0
    external = 0
    for job in cases:
        if job.case_status in (CaseStatus.AWAITING_REVIEW, CaseStatus.PROCESSING):
            awaiting += 1
        if job.case_status == CaseStatus.LEGACY_BULK_ACKNOWLEDGED:
            legacy += 1
        if job.case_status == CaseStatus.REVIEW_DOCUMENTED:
            documented += 1
        for item in job.discrepancy_items:
            if item.status in NON_CLOSURE_ITEM_STATUSES:
                open_items += 1
            if item.status == DiscrepancyItemStatus.AWAITING_EXTERNAL_ACTION:
                external += 1
    return {
        "cases_awaiting_review": awaiting,
        "cases_legacy_bulk_acknowledged": legacy,
        "cases_review_documented": documented,
        "open_items_total": open_items,
        "items_awaiting_external_action": external,
    }
