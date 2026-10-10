# Cloud Healthcare API — FHIR export (Module 2)

JIVANA exports **human-reviewed** medication reconciliation jobs as FHIR R4 transaction bundles (`DetectedIssue`, `MedicationStatement`, `Provenance`).

## Prerequisites

1. Enable `healthcare.googleapis.com` on your hackathon GCP project.
2. Create a **dataset** and **FHIR R4 store** (Console or `gcloud`).
3. Grant the Cloud Run runtime service account:
   - `roles/healthcare.fhirResourceEditor` (scoped to the dataset), or narrower custom role.

## Environment (Cloud Run / local backend)

```env
HEALTHCARE_DATASET_ID=your-dataset
HEALTHCARE_FHIR_STORE_ID=your-fhir-store
HEALTHCARE_LOCATION=us-central1
```

Uses Application Default Credentials (same as Vertex / Document AI on Cloud Run).

## Behavior

- Export runs **only after** a reviewer submits acknowledgment on a `needs_review` job.
- If variables are unset, review still completes; export is skipped (logged).
- If variables are set but the API call fails, `fhir_export_resource` is set to `failed` on the job.

Official docs: [Cloud Healthcare API](https://docs.cloud.google.com/healthcare-api/docs).
