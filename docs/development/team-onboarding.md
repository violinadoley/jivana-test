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

### Minimal local configuration

**Backend** (`backend/.env`):

| Variable | Required locally? | Notes |
|----------|-------------------|--------|
| `GEMINI_API_KEY` | **Yes** (for AI routes) | [Google AI Studio](https://aistudio.google.com/apikey) — team shares one **dev** key or each uses their own |
| `CORS_ORIGINS` | Default OK | `http://localhost:3000` |
| `AUTH_REQUIRED` | Default `false` | Open API for local dev |
| `AGENT_BACKEND` | Default `auto` | Uses Google ADK when installed (`requirements.txt`) |

**Frontend** (`frontend/.env.local`):

| Variable | Required locally? | Notes |
|----------|-------------------|--------|
| `NEXT_PUBLIC_API_URL` | **Yes** | `http://127.0.0.1:8000` |
| `NEXT_PUBLIC_MVP_WORKBENCH` | Recommended `true` | Hackathon / product workbench |
| `NEXT_PUBLIC_FIREBASE_*` | Optional | Needed only for Google sign-in UI |
| `NEXT_PUBLIC_AUTH_REQUIRED` | Default `false` | Match backend if you enforce login |

GCP-backed features (Document AI med rec with PDF, Vertex Search, FHIR export, BigQuery events) need the optional backend vars in [backend/.env.example](../../backend/.env.example) **and** ADC or `GOOGLE_APPLICATION_CREDENTIALS`. Without them, many flows still work with `.txt` fixtures and institutional search corpus.

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
