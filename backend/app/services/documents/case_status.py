from app.schemas.meddocs import CaseStatus, JobStatus, MedReconciliationJob
from app.services.documents.discrepancy_items import has_non_closure_items


def sync_legacy_job_status(job: MedReconciliationJob) -> None:
    """Keep JobStatus in sync with case_status for older clients."""
    if job.case_status == CaseStatus.PROCESSING:
        job.status = JobStatus.PROCESSING
    elif job.case_status == CaseStatus.FAILED:
        job.status = JobStatus.FAILED
    elif job.case_status == CaseStatus.REVIEW_DOCUMENTED:
        job.status = JobStatus.COMPLETED
    elif job.case_status in (
        CaseStatus.AWAITING_REVIEW,
        CaseStatus.LEGACY_BULK_ACKNOWLEDGED,
    ):
        job.status = JobStatus.NEEDS_REVIEW
    elif job.case_status == CaseStatus.DRAFT:
        job.status = JobStatus.NEEDS_REVIEW


def apply_post_pipeline_case_status(job: MedReconciliationJob) -> None:
    """After extraction: always awaiting_review until human finalize path completes."""
    job.case_status = CaseStatus.AWAITING_REVIEW
    if not job.discrepancy_items and (job.discrepancies or job.validation_findings):
        from app.services.documents.discrepancy_items import materialize_discrepancy_items

        job.discrepancy_items = materialize_discrepancy_items(job)
    job.item_review_phase = "in_progress"
    sync_legacy_job_status(job)
    job.review_reasons = _review_reasons(job)


def _review_reasons(job: MedReconciliationJob) -> list[str]:
    reasons: list[str] = []
    if job.reconciliation_used_weak_evidence:
        reasons.append("Reconciliation used vertex_only or low evidence.")
    for d in job.discrepancies:
        reasons.append(f"{d.discrepancy_type.value}: {d.summary}")
    for f in job.validation_findings:
        if f.requires_review:
            reasons.append(f"{f.code}: {f.message}")
    return reasons


def can_finalize(job: MedReconciliationJob) -> tuple[bool, str | None]:
    if job.case_status != CaseStatus.AWAITING_REVIEW:
        return False, "Case must be in awaiting_review to finalize."
    if has_non_closure_items(job):
        return False, "All discrepancy items must be in a closure state."
    if job.reconciliation_used_weak_evidence:
        if not job.attestation or not job.attestation.weak_evidence_acknowledged:
            return False, "Weak evidence attestation required."
    if not job.discrepancy_items:
        if not job.attestation or not job.attestation.no_discrepancies:
            return False, "No-discrepancy attestation required."
    return True, None
