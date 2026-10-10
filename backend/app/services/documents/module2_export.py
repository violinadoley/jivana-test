import logging

from app.schemas.meddocs import MedReconciliationJob

logger = logging.getLogger(__name__)


def on_reconciliation_completed(job: MedReconciliationJob) -> None:
    """Module 2 hook (FHIR / BigQuery) — no-op in Module 1."""
    logger.debug("Module 2 export hook skipped for job_id=%s", job.job_id)
