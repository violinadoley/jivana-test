import logging

from app.core.config import get_settings
from app.schemas.meddocs import MedReconciliationJob
from app.services.healthcare.fhir_export_service import HealthcareFhirExportService

logger = logging.getLogger(__name__)


def on_reconciliation_completed(job: MedReconciliationJob) -> MedReconciliationJob:
    """Module 2: export reconciled job to Cloud Healthcare API FHIR store when configured."""
    settings = get_settings()
    exporter = HealthcareFhirExportService(settings)
    export_id = exporter.export_reconciliation(job)
    if export_id:
        job.fhir_export_resource = export_id
    elif settings.healthcare_fhir_configured:
        job.fhir_export_resource = "failed"
    return job
