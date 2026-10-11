from app.schemas.meddocs import (
    CaseStatus,
    DiscrepancyItemStatus,
    JobStatus,
    MedReconciliationJob,
)
from app.services.documents.case_status import sync_legacy_job_status
from app.services.documents.discrepancy_items import materialize_discrepancy_items


def _mark_open_items_legacy_unreviewed(job: MedReconciliationJob) -> None:
    if not job.legacy_bulk_review:
        return
    for item in job.discrepancy_items:
        if item.status == DiscrepancyItemStatus.OPEN and not item.review_history:
            item.status = DiscrepancyItemStatus.LEGACY_UNREVIEWED


def migrate_job_on_read(job: MedReconciliationJob) -> MedReconciliationJob:
    """Hydrate case fields and legacy bulk handling without fabricating item reviews."""
    if not job.transition_type:
        job.transition_type = "discharge"

    if job.human_review and not job.legacy_bulk_review:
        job.legacy_bulk_review = job.human_review
        job.review_granularity = "legacy_bulk"
        job.case_status = CaseStatus.LEGACY_BULK_ACKNOWLEDGED

    if not job.case_label and job.synthetic_mrn:
        job.case_label = f"Discharge — {job.synthetic_mrn}"

    if not job.discrepancy_items and (
        job.discrepancies or any(f.requires_review for f in job.validation_findings)
    ):
        initial = (
            DiscrepancyItemStatus.LEGACY_UNREVIEWED
            if job.legacy_bulk_review
            else DiscrepancyItemStatus.OPEN
        )
        job.discrepancy_items = materialize_discrepancy_items(job, initial_status=initial)

    _mark_open_items_legacy_unreviewed(job)

    if job.case_status == CaseStatus.DRAFT and job.documents:
        if job.status == JobStatus.FAILED:
            job.case_status = CaseStatus.FAILED
        elif job.status == JobStatus.PROCESSING:
            job.case_status = CaseStatus.PROCESSING
        elif job.legacy_bulk_review:
            job.case_status = CaseStatus.LEGACY_BULK_ACKNOWLEDGED
        elif job.status in (JobStatus.NEEDS_REVIEW, JobStatus.COMPLETED):
            if job.human_review and job.review_granularity == "legacy_bulk":
                job.case_status = CaseStatus.LEGACY_BULK_ACKNOWLEDGED
            elif job.human_review and not job.discrepancy_items:
                job.case_status = CaseStatus.AWAITING_REVIEW
            else:
                job.case_status = CaseStatus.AWAITING_REVIEW

    if job.human_review and job.review_granularity == "legacy_bulk":
        job.case_status = CaseStatus.LEGACY_BULK_ACKNOWLEDGED

    if job.case_status == CaseStatus.REVIEW_DOCUMENTED or (
        job.status == JobStatus.COMPLETED and job.finalized_at and not job.legacy_bulk_review
    ):
        job.case_status = CaseStatus.REVIEW_DOCUMENTED

    sync_legacy_job_status(job)
    return job
