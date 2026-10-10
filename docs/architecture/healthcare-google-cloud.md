# Google Cloud Healthcare API (team reference)

**Competition direction:** healthcare (product idea still chosen by the team).  
**Primary documentation:** [Cloud Healthcare API docs](https://docs.cloud.google.com/healthcare-api/docs)

This page explains how the **Cloud Healthcare API** relates to this starter. It does **not** define a product or require enabling the API until an approved architecture says so.

---

## What the Healthcare API is

Managed Google Cloud service for **clinical and imaging data** using industry standards:

| Modality | Standard | Typical use |
|----------|----------|-------------|
| **FHIR stores** | HL7 FHIR (R4, STU3, DSTU2) | Patients, encounters, observations, care plans—interop with EHR-style data |
| **DICOM stores** | DICOMweb | Medical imaging (CT, MRI, etc.) |
| **HL7v2 stores** | HL7 v2.x | Legacy hospital messaging (ADT, ORU, etc.) |
| **De-identification** | API on dataset/store | Redact PHI for analytics/research workflows |

Hierarchy: **GCP project → dataset → store** (FHIR / DICOM / HL7v2). See [Projects, datasets, and data stores](https://docs.cloud.google.com/healthcare-api/docs/projects-datasets-data-stores).

REST base pattern (FHIR example):

```text
https://healthcare.googleapis.com/v1/projects/PROJECT/locations/LOCATION/datasets/DATASET/fhirStores/STORE/fhir/...
```

Overview: [Introduction](https://docs.cloud.google.com/healthcare-api/docs/introduction) · [API structure](https://docs.cloud.google.com/healthcare-api/docs/api-structure) · [FHIR concepts](https://docs.cloud.google.com/healthcare-api/docs/concepts/fhir).

---

## How this differs from what the starter already has

| This starter (today) | Cloud Healthcare API |
|----------------------|----------------------|
| **Firestore** — app metadata, activity feed, session-ish data | **FHIR/DICOM/HL7** — regulated clinical/imaging payloads |
| **FastAPI** — your business logic and Gemini calls | **Healthcare API** — standards-compliant clinical storage and search |
| **Firebase Auth** — user login | **IAM + audit logs** — who can access which dataset/store |
| **Synthetic / demo data** assumed | **Real PHI** requires strict design (see below) |
| **MedDocs Module 1** (implemented) — Firestore jobs, GCS uploads, optional Document AI + Vertex ADC for `/api/v1/meddocs/*` | **Module 2 (deferred)** — FHIR export to Healthcare API / BigQuery |

Most healthcare hackathon builds use a **hybrid**:

- **Healthcare API** (or FHIR-shaped mock) for “clinical record” semantics judges expect in healthcare tracks.
- **Existing Cloud Run + FastAPI** as the **BFF** (backend-for-frontend): auth, validation, Gemini, orchestration—**not** exposing Healthcare API credentials to the browser.
- **Gemini** for summarization, triage support, documentation assist—on **de-identified or synthetic** data unless you have explicit compliance sign-off.

---

## Pairing with Gemini and other Google AI (conceptual)

Common patterns (choose in architecture proposal, not here):

- **Gemini** on text derived from FHIR resources (after access control and minimization).
- **Document AI** for unstructured clinical PDFs → structured fields → FHIR or app storage.
- **BigQuery** export from FHIR/DICOM metadata for analytics ([docs](https://docs.cloud.google.com/healthcare-api/docs/introduction) — export paths).
- **Vertex AI** if you move from API-key Gemini to enterprise Vertex for healthcare-adjacent deployments.

Keep **model calls on the backend** (same as current starter); never send PHI to the client or to third-party analytics (PostHog, etc.) without a documented policy.

---

## Security and hackathon defaults

- Treat **PHI as out of scope** for public repos, CI logs, PostHog, and demo videos unless the team deliberately designs otherwise.
- Use **synthetic FHIR bundles** or public sample datasets for demos and `ai-evals/`.
- Enable **Cloud Healthcare API** only in your **hackathon GCP project**; separate from personal/production accounts.
- Prefer **least-privilege IAM** on datasets/stores; FastAPI service account accesses Healthcare API, not end users directly.
- De-identification API is for **defined** redaction workflows—not a substitute for legal/compliance review.

See also [docs/security-defaults.md](../security-defaults.md) and `.cursor/rules/security.mdc`.

---

## Implementation path (when approved)

1. Enable API: `healthcare.googleapis.com` in the same GCP project as Cloud Run (or document a dedicated clinical project if split).
2. Create **dataset + FHIR store** (most common for app-style demos) via console, `gcloud`, or Terraform if the team adds IaC.
3. Add **`google-cloud-healthcare`** (or REST) in **backend** only; new routes under `backend/app/api/` and services under `backend/app/services/`.
4. Wire **Cloud Run** runtime SA with roles such as `roles/healthcare.fhirResourceEditor` / reader scopes **narrowed** to one dataset—exact roles per approved design.
5. Extend **CI** with mocks; no live PHI in pytest default runs.
6. Update [technology-capability-matrix.md](./technology-capability-matrix.md) status from **Absent** to **Verified** when integrated.

Official quickstarts: linked from [docs home](https://docs.cloud.google.com/healthcare-api/docs).

---

## Developer tools (Cursor / MCP)

- **No dedicated Cloud Healthcare API remote MCP** is listed in [Google Cloud supported MCP products](https://docs.cloud.google.com/mcp/supported-products) (as of starter 1.0.0 research).
- Prefer **official docs** ([docs.cloud.google.com/healthcare-api/docs](https://docs.cloud.google.com/healthcare-api/docs)), **Context7**, or **Developer Knowledge API MCP** for API syntax.
- Runtime integration: **Python client library / REST from FastAPI**, not MCP.

See [mcp-and-tooling-catalogue.md](./mcp-and-tooling-catalogue.md).

---

## AI Builder Cup category hint

Healthcare solutions often align with **BFSI** (risk, compliance, documents) or **Future of Work & Enterprise Productivity** (clinical workflow, search)—use category **suggested** technologies only as a checklist, not a mandatory stack. Map your **approved** architecture to the matrix before adding services.

---

## Related in this repo

- [technology-decision-process.md](./technology-decision-process.md)
- [technology-capability-matrix.md](./technology-capability-matrix.md)
- [docs/architecture.md](../architecture.md)
