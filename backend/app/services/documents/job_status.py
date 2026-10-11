from app.schemas.meddocs import (
    JobStatus,
    MedDiscrepancy,
    MedReconciliationJob,
    ValidationFinding,
)
from app.services.documents.case_status import apply_post_pipeline_case_status
from app.services.documents.discrepancy_items import materialize_discrepancy_items


def compute_job_status(
    discrepancies: list[MedDiscrepancy],
    findings: list[ValidationFinding],
    reconciliation_used_weak_evidence: bool,
) -> JobStatus:
    """Legacy helper: MVP never auto-completes without human finalize."""
    del discrepancies, findings, reconciliation_used_weak_evidence
    return JobStatus.NEEDS_REVIEW


def apply_status_to_job(job: MedReconciliationJob) -> None:
    job.discrepancy_items = materialize_discrepancy_items(job)
    apply_post_pipeline_case_status(job)
