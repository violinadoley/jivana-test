# Team onboarding — JIVANA

How to run the app locally, which secrets to share with teammates, and how the stack fits together.

**Inviting someone?** Copy the blurb from [team-invite-message.md](./team-invite-message.md).

**Do not commit** `.env`, `.env.local`, service account JSON, or API keys. Share secrets through your team password manager or GitHub Actions secrets/variables — never in Slack or email in plain text.

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| **Node.js** | 22.x (CI uses 22) | Frontend, Playwright |
| **Python** | 3.11+ (CI uses 3.11) | Backend API |
| **npm** | 10+ | Frontend packages |
| **Git** | 2.x | Branching / PR workflow |

Optional for full GCP parity locally:

- [Google Cloud SDK](https://cloud.google.com/sdk) (`gcloud auth application-default login`) for Document AI, Vertex Search, BigQuery, FHIR export without a service account file.
- Or set `GOOGLE_APPLICATION_CREDENTIALS` to a **dev** service account JSON (never commit the file).

## Quick start (two terminals)

```bash
git clone git@github.com:violinadoley/JIVANA.git
cd JIVANA

# Terminal 1 — API
cd backend
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp -n .env.example .env
# Edit backend/.env — at minimum set GEMINI_API_KEY=
uvicorn app.main:app --reload --reload-dir app --port 8000

# Terminal 2 — UI
cd frontend
npm ci
cp -n .env.local.example .env.local
# Edit frontend/.env.local — NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
npm run dev
```

Open [http://localhost:3000/dashboard](http://localhost:3000/dashboard). API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

Or print the same steps: `./scripts/dev.sh`.

### Three setup tiers (pick one)

#### Tier A — “It runs” (smoke test)

Enough to load the UI and hit AI routes. **Data is in-memory** on the API process (med rec cases and copilot sessions **reset when you restart uvicorn**).

| Where | Variables |
|-------|-----------|
| **Backend** | `GEMINI_API_KEY` |
| **Frontend** | `NEXT_PUBLIC_API_URL=http://127.0.0.1:8000`, `NEXT_PUBLIC_MVP_WORKBENCH=true` |

Works without Firebase or GCP project credentials. Search still returns **institutional corpus** hits; Vertex Search, Document AI PDF, FHIR, BigQuery, and GCS uploads are off.

#### Tier B — **Recommended for teammates** (matches how you work day to day)

Same as Tier A, plus **Firebase** so cases, activity, copilot sessions, and uploads behave like cloud (shared project, data survives restarts).

**Backend** (`backend/.env`):

| Variable | Notes |
|----------|--------|
| `GEMINI_API_KEY` | Dev key from vault or AI Studio |
| `FIREBASE_PROJECT_ID` | Same GCP/Firebase project as the team (e.g. `project-bf77a013-c0b3-413c-a75`) |
| `FIREBASE_STORAGE_BUCKET` | e.g. `{project}.firebasestorage.app` |
| `GCP_PROJECT_ID` | Usually same as Firebase project (Vertex / optional GCP APIs) |
| Auth to Firestore | **`gcloud auth application-default login`** in the dev project, **or** `GOOGLE_APPLICATION_CREDENTIALS=/path/to/dev-sa.json` (never commit the file) |

**Frontend** (`frontend/.env.local`):

| Variable | Notes |
|----------|--------|
| `NEXT_PUBLIC_API_URL` | `http://127.0.0.1:8000` |
| `NEXT_PUBLIC_MVP_WORKBENCH` | `true` |
| `NEXT_PUBLIC_FIREBASE_API_KEY` | From Firebase console → Project settings → Your apps → Web |
| `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN` | `{project}.firebaseapp.com` |
| `NEXT_PUBLIC_FIREBASE_PROJECT_ID` | Same as backend |
| `NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET` | Same as backend |
| `NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID` | From Firebase web config |
| `NEXT_PUBLIC_FIREBASE_APP_ID` | From Firebase web config |
| `NEXT_PUBLIC_AUTH_REQUIRED` | `false` locally unless testing login-only mode |

Sync GitHub deploy vars from Firebase: `./scripts/sync-firebase-github-vars.sh YOUR_GCP_PROJECT_ID` (maintainers).

#### Tier C — **Full GCP parity** (optional)

Tier B **plus** copy production integration IDs from GitHub Variables (or team vault) into `backend/.env`:

| Variable | Enables |
|----------|---------|
| `DOCUMENT_AI_PROCESSOR_ID` + `DOCUMENT_AI_LOCATION` | PDF/image med rec intake |
| `VERTEX_SEARCH_DATA_STORE_ID` (+ location/serving config) | Live Vertex AI Search |
| `BIGQUERY_DATASET_ID` | Productivity events to BigQuery |
| `HEALTHCARE_DATASET_ID`, `HEALTHCARE_FHIR_STORE_ID`, `HEALTHCARE_LOCATION` | FHIR export after sign-off |
| `SMART_*` | SMART config/redirect testing against real iss |
| ADC or service account | Required for all of the above locally |

Use the same values as [environment-variables.md](./environment-variables.md) / GitHub Actions Variables. Region for this project is typically **`asia-south1`**.

**Defaults that are fine everywhere:** `CORS_ORIGINS=http://localhost:3000`, `AUTH_REQUIRED=false`, `AGENT_BACKEND=auto`.

## What to share with teammates

### Share via password manager (secrets)

| Secret | Who needs it |
|--------|----------------|
| `GEMINI_API_KEY` | Anyone running AI locally |
| `GEMINI_API_KEY` in GCP Secret Manager | Already wired for Cloud Run deploy — ops only |
| Dev service account JSON (if used) | Devs testing Document AI / FHIR locally — **file only, not Git** |

### Share as repo documentation (non-secret)

| Item | Where |
|------|--------|
| Firebase **web** client config (`NEXT_PUBLIC_FIREBASE_*`) | Not secret; sync from Firebase console or `./scripts/sync-firebase-github-vars.sh` |
| Production URLs | README — Hosting `.web.app`, Cloud Run API |
| GitHub Actions **Variables** | [github-google-oidc.md](../setup/github-google-oidc.md) — team leads / deploy access |

### Never share in Git or public chat

- `.env`, `.env.local`, `.env.production`
- OAuth client **secrets**
- Service account private keys
- PostHog project keys (rotate if leaked — [posthog.md](../setup/posthog.md))

## Tech stack — what runs where

| Layer | Technology | Purpose in JIVANA |
|-------|------------|-------------------|
| **UI** | Next.js 16, React 19, TypeScript | Marketing home, `/dashboard` workspace, `/smart/launch` |
| **UI styling** | Tailwind CSS 4, shadcn/ui (Base UI) | Components, layout, accessibility |
| **UI hosting** | Firebase Hosting (static export) | CDN, HTTPS, `.web.app` URL |
| **API** | FastAPI, Uvicorn, Pydantic Settings | BFF: auth, med rec, AI, search, analytics |
| **API hosting** | Cloud Run | Autoscale, ADC to Google APIs, Secret Manager for Gemini |
| **AI (models)** | Gemini 2.5 Flash via `google-genai` | Copilot, meetings, research, workflows, med extract |
| **AI (agents)** | Google ADK (`google-adk`) in-process on Cloud Run | Tool-using agents; **not** used for med rec reconciliation logic |
| **Document intake** | Document AI + Vertex (optional) | PDF/layout blocks; plain text bypasses Document AI |
| **Search** | Vertex AI Search (Discovery Engine) + local JSON corpus | Enterprise search tab |
| **Data** | Firestore (Admin SDK) | Activity, copilot sessions, med rec jobs |
| **Files** | Cloud Storage (Firebase bucket) | Uploads via API |
| **Analytics** | BigQuery (optional) | Productivity event stream |
| **Interop** | Cloud Healthcare API (FHIR R4) | Export after human sign-off |
| **EHR embed** | SMART on FHIR config + launch page | Demo redirect; OAuth token exchange not implemented |
| **Auth** | Firebase Auth (Google) | Optional; ID token verified on API when sent |
| **CI** | GitHub Actions | Lint, test, deploy on `develop` |
| **E2E** | Playwright | Local preview + post-deploy hosting smoke |

Optional / planned: **Vertex AI Agent Engine** (hosted ADK) — env hook only; production uses in-process ADK. See [vertex-ai-agent-engine.md](../setup/vertex-ai-agent-engine.md).

## Wiring consistency (monorepo)

These paths are the source of truth and are kept aligned with CI/deploy:

| Concern | Location |
|---------|----------|
| API routes | `backend/app/api/router.py` — health, meddocs, copilot, search, platform, **smart**, workflows, … |
| Settings / env | `backend/app/core/config.py` ↔ `backend/.env.example` ↔ `.github/workflows/deploy.yml` |
| Frontend API base | `frontend/lib/api.ts` ← `NEXT_PUBLIC_API_URL` |
| MVP workbench flag | `frontend/lib/mvp-workbench.ts` ← `NEXT_PUBLIC_MVP_WORKBENCH` |
| Deploy vars | GitHub Actions Variables → Cloud Run env + Hosting build ([environment-variables.md](./environment-variables.md)) |
| Med rec never ADK | Intake/reconcile in `services/documents/`; ADK only under `app/ai/adk/` for enterprise agents |

Backend tests (`pytest`) and frontend `npm run build` + Playwright smoke should pass before merging to `develop`.

## Verify your setup

```bash
# Backend quality (from backend/)
ruff check app tests && mypy app && pytest -q

# Frontend quality (from frontend/)
npm run lint && npm run typecheck && npm run build

# With API running on :8000
API_BASE_URL=http://127.0.0.1:8000 ./scripts/smoke-api.sh
API_BASE_URL=http://127.0.0.1:8000 ./scripts/verify-platform.sh --probe

# E2E (starts Next preview automatically)
cd frontend && npm run test:e2e
```

Production checks: [verify-integrations.md](../setup/verify-integrations.md).

## Git and contributors

- Branch from `develop`; merge via PR. See [CONTRIBUTING.md](../../CONTRIBUTING.md).
- Commit under **your** GitHub identity. Do **not** add `Co-authored-by: Cursor <cursoragent@cursor.com>` — GitHub counts co-authors as contributors.
- In Cursor: disable automatic co-author trailers for this repo.

## Deeper reading

- [jivana-design-and-operations.md](../product/jivana-design-and-operations.md) — product architecture and flows
- [environment-variables.md](./environment-variables.md) — full variable reference
- [testing-strategy.md](./testing-strategy.md) — pytest, Playwright, ai-evals
