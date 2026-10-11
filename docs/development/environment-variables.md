# Environment variables reference

Canonical list for **local** (`.env` / `.env.local`) and **production** (GitHub Actions Variables → Cloud Run / Hosting build).

## Backend — `backend/.env`

Copy from [backend/.env.example](../../backend/.env.example).

| Variable | Local | Cloud Run | Description |
|----------|-------|-----------|-------------|
| `GEMINI_API_KEY` | Dev key | Secret Manager `GEMINI_API_KEY:latest` | Gemini API (local dev). Cloud also uses Vertex ADC when `ENVIRONMENT=cloud`. |
| `GEMINI_MODEL` | Optional | Set in deploy | Default `gemini-2.5-flash` |
| `AGENT_BACKEND` | `auto` | `auto` | `auto` \| `adk` \| `legacy` for copilot/research/workflows |
| `VERTEX_AGENT_ENGINE_ID` | Empty | Optional var | Stub only until Agent Engine is wired |
| `SMART_CLIENT_ID` | Optional | GitHub var | OAuth Web client id |
| `SMART_FHIR_ISS` | Optional | GitHub var | FHIR base URL for SMART config |
| `SMART_APP_LAUNCH_URL` | Optional | GitHub var | Hosting `/smart/launch` URL |
| `FIREBASE_PROJECT_ID` | Optional | Deploy | Firestore / Storage / ADC project |
| `FIREBASE_STORAGE_BUCKET` | Optional | Deploy | GCS bucket for uploads |
| `GOOGLE_APPLICATION_CREDENTIALS` | Optional | Not used on Run | Path to SA JSON for local GCP APIs |
| `GCP_PROJECT_ID` | Optional | Deploy | Vertex / Document AI / BQ project |
| `VERTEX_LOCATION` | Optional | Deploy | e.g. `asia-south1` |
| `DOCUMENT_AI_PROCESSOR_ID` | Optional | GitHub var | Med rec PDF/image intake |
| `VERTEX_SEARCH_DATA_STORE_ID` | Optional | GitHub var | Discovery Engine data store |
| `BIGQUERY_DATASET_ID` | Optional | GitHub var | Productivity events dataset |
| `HEALTHCARE_*` | Optional | GitHub var | FHIR store export |
| `AUTH_REQUIRED` | `false` | Deploy | Require Bearer token on API |
| `CORS_ORIGINS` | localhost | Deploy | Comma-separated origins |
| `ENVIRONMENT` | `development` | `cloud` | Error masking, OpenAPI |

## Frontend — `frontend/.env.local`

Copy from [frontend/.env.local.example](../../frontend/.env.local.example).

| Variable | Local | Hosting build | Description |
|----------|-------|---------------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://127.0.0.1:8000` | `PUBLIC_API_URL` var | Cloud Run base URL (no `/docs`) |
| `NEXT_PUBLIC_MVP_WORKBENCH` | `true` | `true` in deploy | MVP med rec workbench vs legacy tabs |
| `NEXT_PUBLIC_SITE_URL` | Optional | GitHub var | Open Graph canonical URL |
| `NEXT_PUBLIC_FIREBASE_*` | From Firebase console | GitHub vars | Web app config (public, not secret) |
| `NEXT_PUBLIC_AUTH_REQUIRED` | `false` | Deploy | Force sign-in in UI |
| `NEXT_PUBLIC_POSTHOG_*` | Optional | Optional vars | Analytics |

## GitHub Actions Variables (deploy)

Repository **Settings → Secrets and variables → Actions → Variables**. Full deploy list: [github-google-oidc.md](../setup/github-google-oidc.md).

Notable additions for JIVANA:

| Variable | Purpose |
|----------|---------|
| `PUBLIC_API_URL` | Cloud Run URL → `NEXT_PUBLIC_API_URL` at build |
| `SMART_APP_LAUNCH_URL` | SMART redirect target |
| `SMART_CLIENT_ID` | Registered OAuth Web client |
| `SMART_FHIR_ISS` | FHIR issuer URL |
| `NEXT_PUBLIC_SITE_URL` | OG / metadata base |
| `VERTEX_AGENT_ENGINE_ID` | Optional; leave empty until Agent Engine exists |

Secrets (not variables): `GEMINI_API_KEY` in GCP Secret Manager, referenced by deploy workflow.
