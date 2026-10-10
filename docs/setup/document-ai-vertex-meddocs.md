# Document AI + Vertex (MedDocs Module 1)

**Prototype only** — use **synthetic sample documents** in git, CI, and demo video. This is not a compliance-certified clinical system. Production use with real PHI requires a **separate** security and compliance assessment (not claimed in this repository).

## APIs to enable

In the same GCP project as Cloud Run:

```bash
gcloud services enable documentai.googleapis.com aiplatform.googleapis.com
```

## Document AI processor (optional)

| `DOCUMENT_AI_PROCESSOR_ID` | Behavior |
|--------------------------|----------|
| **Empty / unset** | Vertex-only intake path; blocks marked `vertex_only`; reconciliation routes to **needs_review** when weak evidence is used. |
| **Set** | Server **must** verify processor exists in `DOCUMENT_AI_LOCATION`. Invalid → `DOCUMENT_AI_MISCONFIGURED` (no silent fallback). |

Create a processor (example — adjust type/region to your project):

```bash
gcloud documentai processors create \
  --location=us \
  --type=FORM_PARSER_PROCESSOR \
  --display-name=meddocs-form-parser
```

Set GitHub / Cloud Run variables:

- `DOCUMENT_AI_PROCESSOR_ID` — full processor resource name or ID per client library
- `DOCUMENT_AI_LOCATION` — e.g. `us` or `eu`
- `GCP_LOCATION` — Vertex region (e.g. `asia-south1`, `us-central1`)

## IAM (Cloud Run runtime service account)

Minimum for Module 1:

- `roles/documentai.apiUser` (when processor configured)
- `roles/aiplatform.user`
- Existing Storage / Firestore roles from [firebase-backend.md](./firebase-backend.md)

## Environment variables

Add to `backend/.env` locally and Cloud Run deploy env:

| Variable | Required | Notes |
|----------|----------|--------|
| `GCP_PROJECT_ID` | For Vertex/DocAI | Defaults to `FIREBASE_PROJECT_ID` if unset |
| `GCP_LOCATION` | For Vertex | |
| `DOCUMENT_AI_PROCESSOR_ID` | No | Empty = Vertex-only path |
| `DOCUMENT_AI_LOCATION` | When DocAI set | |

Generic **`GEMINI_API_KEY`** remains for `/api/v1/ai/generate` only. MedDocs uses **Vertex ADC** on Cloud Run.

## Verify

1. Local: leave `DOCUMENT_AI_PROCESSOR_ID` empty → run meddocs pytest (mocked).
2. Cloud: set processor → upload synthetic PDF bundle via dashboard → check job status and review queue.
