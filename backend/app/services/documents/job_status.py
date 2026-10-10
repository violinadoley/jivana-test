from app.schemas.meddocs import JobStatus, MedDiscrepancy, MedReconciliationJob, ValidationFinding


def compute_job_status(
    discrepancies: list[MedDiscrepancy],
    findings: list[ValidationFinding],
    reconciliation_used_weak_evidence: bool,
) -> JobStatus:
    if any(f.requires_review for f in findings):
        return JobStatus.NEEDS_REVIEW
    if discrepancies:
        return JobStatus.NEEDS_REVIEW
    if reconciliation_used_weak_evidence:
        return JobStatus.NEEDS_REVIEW
    return JobStatus.COMPLETED


def apply_status_to_job(job: MedReconciliationJob) -> None:
    job.status = compute_job_status(
        job.discrepancies,
        job.validation_findings,
        job.reconciliation_used_weak_evidence,
    )
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
