import logging
import uuid
from typing import Any

from app.core.config import Settings
from app.schemas.meddocs import CaseStatus, DiscrepancyType, MedReconciliationJob

logger = logging.getLogger(__name__)


def build_reconciliation_bundle(job: MedReconciliationJob) -> dict[str, Any]:
    """FHIR R4 Bundle for audit / interop (synthetic-friendly)."""
    patient_ref = f"Patient/jivana-{job.job_id[:8]}"
    entries: list[dict[str, Any]] = []

    for index, disc in enumerate(job.discrepancies):
        code = disc.discrepancy_type.value
        entries.append(
            {
                "fullUrl": f"urn:uuid:detected-{job.job_id}-{index}",
                "resource": {
                    "resourceType": "DetectedIssue",
                    "status": "preliminary",
                    "code": {
                        "text": code,
                    },
                    "severity": "high"
                    if disc.discrepancy_type
                    in (DiscrepancyType.DOSE_MISMATCH, DiscrepancyType.OMITTED_MED)
                    else "moderate",
                    "detail": disc.summary,
                    "patient": {"reference": patient_ref},
                },
                "request": {"method": "POST", "url": "DetectedIssue"},
            }
        )

    med_index = 0
    for doc_id, meds in job.medications_by_document.items():
        for med in meds:
            med_index += 1
            entries.append(
                {
                    "fullUrl": f"urn:uuid:med-{job.job_id}-{med_index}",
                    "resource": {
                        "resourceType": "MedicationStatement",
                        "status": "active",
                        "subject": {"reference": patient_ref},
                        "medicationCodeableConcept": {
                            "text": med.medication_name,
                        },
                        "dosage": [
                            {
                                "text": " ".join(
                                    filter(
                                        None,
                                        [med.dose, med.strength, med.route, med.frequency],
                                    )
                                )
                                or None,
                            }
                        ],
                        "note": [
                            {
                                "text": (
                                    f"document_id={doc_id}; evidence={med.evidence_status.value}"
                                ),
                            }
                        ],
                    },
                    "request": {"method": "POST", "url": "MedicationStatement"},
                }
            )

    review = job.human_review
    if review:
        review_note = review.note or "Human review recorded"
        reviewer = review.reviewer_uid or "jivana-reviewer"
        reviewed_at = review.reviewed_at
    elif job.case_status == CaseStatus.REVIEW_DOCUMENTED:
        att_note = job.attestation.note if job.attestation else None
        review_note = att_note or "Per-item review documented"
        reviewer = job.finalized_by_uid or job.finalized_by_display or "jivana-reviewer"
        reviewed_at = job.finalized_at
    else:
        review_note = "Pending review"
        reviewer = "jivana-system"
        reviewed_at = None
    entries.append(
        {
            "fullUrl": f"urn:uuid:prov-{job.job_id}",
            "resource": {
                "resourceType": "Provenance",
                "target": [{"reference": patient_ref}],
                "recorded": job.metrics.completed_at or job.metrics.started_at,
                "activity": {
                    "text": "medication-reconciliation",
                },
                "agent": [
                    {
                        "type": {"text": "author"},
                        "who": {"display": reviewer},
                    }
                ],
                "entity": [
                    {
                        "role": "source",
                        "what": {"display": f"job_id={job.job_id}"},
                    }
                ],
                "signature": [
                    {
                        "type": [{"text": "human acknowledgment"}],
                        "when": reviewed_at,
                        "who": {"display": review_note},
                    }
                ],
            },
            "request": {"method": "POST", "url": "Provenance"},
        }
    )

    return {
        "resourceType": "Bundle",
        "type": "transaction",
        "entry": entries,
    }


class HealthcareFhirExportService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    @property
    def configured(self) -> bool:
        return bool(
            self._settings.healthcare_dataset_id
            and self._settings.healthcare_fhir_store_id
            and self._settings.effective_gcp_project_id
        )

    def export_reconciliation(self, job: MedReconciliationJob) -> str | None:
        if job.case_status != CaseStatus.REVIEW_DOCUMENTED and job.human_review is None:
            logger.info("Skipping FHIR export until review documented for job_id=%s", job.job_id)
            return None
        if not self.configured:
            logger.info(
                "Healthcare API FHIR store not configured; skipping export for job_id=%s",
                job.job_id,
            )
            return None

        bundle = build_reconciliation_bundle(job)
        project = self._settings.effective_gcp_project_id
        location = self._settings.healthcare_location
        dataset = self._settings.healthcare_dataset_id
        store = self._settings.healthcare_fhir_store_id
        base = (
            f"https://healthcare.googleapis.com/v1/projects/{project}/locations/{location}"
            f"/datasets/{dataset}/fhirStores/{store}/fhir"
        )

        try:
            from google.auth import default
            from google.auth.transport.requests import AuthorizedSession

            credentials, _ = default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
            session = AuthorizedSession(credentials)
            response = session.post(
                base,
                json=bundle,
                headers={"Content-Type": "application/fhir+json"},
                timeout=30,
            )
            if response.status_code >= 400:
                logger.error(
                    "FHIR export failed status=%s body=%s",
                    response.status_code,
                    response.text[:500],
                )
                return None
            resource_id = response.headers.get("Content-Location") or str(uuid.uuid4())
            logger.info("FHIR export succeeded job_id=%s resource=%s", job.job_id, resource_id)
            return resource_id
        except Exception:
            logger.exception("FHIR export error for job_id=%s", job.job_id)
            return None
