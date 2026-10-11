# JIVANA

**Healthcare enterprise knowledge workspace** — medication reconciliation with human sign-off, intelligent search, copilot, meetings, research, and agentic workflows on **Google Cloud**.

| | |
|---|---|
| **Live app** | [Dashboard](https://project-bf77a013-c0b3-413c-a75.web.app/dashboard) |
| **SMART launch** | [/smart/launch](https://project-bf77a013-c0b3-413c-a75.web.app/smart/launch) |
| **API** | Cloud Run base URL in GitHub var `PUBLIC_API_URL`; Swagger at `BACKEND_API_URL` or `{API}/docs` |

## Documentation map

| Doc | Audience |
|-----|----------|
| **[Team onboarding](docs/development/team-onboarding.md)** | New developers — clone, env, secrets, stack |
| **[Environment variables](docs/development/environment-variables.md)** | Full `.env` / GitHub Variables reference |
| **[Design & operations](docs/product/jivana-design-and-operations.md)** | Product architecture, request flows, GCP mapping |
| **[Verify integrations](docs/setup/verify-integrations.md)** | Post-deploy smoke and platform probes |
| **[CONTRIBUTING.md](CONTRIBUTING.md)** | Branching, PRs, **git author / no Cursor co-author** |

## Tech stack (what we use and why)

| Layer | Technology | Role in JIVANA |
|-------|------------|----------------|
| **Frontend** | Next.js 16, React 19, TypeScript | Static export to Firebase Hosting; workspace UI |
| **UI** | Tailwind CSS 4, shadcn/ui | Layout, forms, med rec workbench |
| **API** | FastAPI, Python 3.11+, Uvicorn | Single BFF — auth, med rec, AI, search, FHIR |
| **AI models** | Gemini 2.5 Flash (`google-genai`) | All server-side generation and structured extract |
| **AI agents** | Google ADK (`google-adk`) on Cloud Run | Copilot, research, meetings, workflow planner |
| **Documents** | Document AI, Vertex (ADC) | PDF/image intake; plain text uses direct extract |
| **Search** | Vertex AI Search + institutional JSON | Enterprise search tab |
| **Database** | Firestore (Firebase Admin SDK) | Jobs, sessions, activity — no client-side DB access |
| **Storage** | Google Cloud Storage | File uploads via API |
| **Analytics** | BigQuery (optional) | Productivity events |
| **Clinical interop** | Cloud Healthcare API (FHIR R4) | Bundle export after review |
| **EHR embed** | SMART on FHIR (config + launch page) | Demo launch; full OAuth not implemented |
| **Auth** | Firebase Auth (Google) | Optional ID tokens to API |
| **Deploy** | Cloud Run + Firebase Hosting | GitHub Actions OIDC, no keys in repo |
| **Quality** | pytest, ruff, mypy, ESLint, Playwright, ai-evals | CI on every PR |

Vertex **Agent Engine** is optional future hosting for ADK ([docs](docs/setup/vertex-ai-agent-engine.md)); production uses **in-process ADK** today.

## Repository layout

```text
frontend/                 Next.js app (App Router, static export)
backend/app/              FastAPI — api/, services/, ai/ (prompts + ADK)
backend/tests/            Pytest
docs/                     Architecture, setup, runbooks, product
ai-evals/regression/      Prompt / AI regression harness
scripts/                  dev.sh, smoke-api.sh, verify-platform.sh
.github/workflows/        ci.yml, deploy.yml, deploy-frontend.yml
```

## Local development

**Requirements:** Node 22, Python 3.11+, npm. See [team onboarding](docs/development/team-onboarding.md) for details.

```bash
git clone git@github.com:violinadoley/JIVANA.git
cd JIVANA

# Backend
cd backend && python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env    # set GEMINI_API_KEY
uvicorn app.main:app --reload --reload-dir app --port 8000

# Frontend (new terminal)
cd frontend && npm ci
cp .env.local.example .env.local    # NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
npm run dev
```

- UI: [http://localhost:3000](http://localhost:3000) · API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Helper: `./scripts/dev.sh`

### Teammate checklist

1. Copy `backend/.env.example` → `backend/.env` and `frontend/.env.local.example` → `frontend/.env.local`.
2. **Minimum:** `GEMINI_API_KEY` + `NEXT_PUBLIC_API_URL=http://127.0.0.1:8000` + `NEXT_PUBLIC_MVP_WORKBENCH=true` (AI works; med rec lives in API memory until restart).
3. **Recommended:** Firebase web config on the frontend + `FIREBASE_PROJECT_ID` / storage bucket on the backend + `gcloud auth application-default login` (persistent Firestore, like prod).
4. **Full integrations:** Document AI, Vertex Search, Healthcare FHIR, BigQuery IDs from the team vault — see [team onboarding](docs/development/team-onboarding.md) Tier B/C.

Full variable list: [environment-variables.md](docs/development/environment-variables.md).

## Dependencies

| File | Purpose |
|------|---------|
| [backend/requirements.txt](backend/requirements.txt) | Production API (FastAPI, google-genai, google-adk, Firebase, Document AI, Discovery Engine, BigQuery) |
| [backend/requirements-dev.txt](backend/requirements-dev.txt) | pytest, ruff, mypy, bandit, pip-audit |
| [frontend/package.json](frontend/package.json) | Next.js, Firebase client, Playwright (dev) |

Install dev tooling: `pip install -r backend/requirements-dev.txt` and `npm ci` in `frontend/`.

## Testing

```bash
cd backend && ruff check app tests && mypy app && pytest -q
cd frontend && npm run lint && npm run typecheck && npm run build && npm run test:e2e
```

Strategy: [docs/development/testing-strategy.md](docs/development/testing-strategy.md).

## Git workflow and contributors

- Work on `feature/*` or `fix/*` from **`develop`**; merge via PR with green CI.
- **`develop`** deploys API + frontend to GCP.
- Commits must use **your** GitHub user. Do **not** add `Co-authored-by: Cursor <cursoragent@cursor.com>` ([CONTRIBUTING.md](CONTRIBUTING.md)).

## CI/CD

| Workflow | Trigger |
|----------|---------|
| [ci.yml](.github/workflows/ci.yml) | PR and push to `main` / `develop` |
| [deploy.yml](.github/workflows/deploy.yml) | Push to `develop` → Cloud Run |
| [deploy-frontend.yml](.github/workflows/deploy-frontend.yml) | Push to `develop` → Hosting + hosted Playwright smoke |

Setup: [github-google-oidc.md](docs/setup/github-google-oidc.md) · [firebase-hosting.md](docs/setup/firebase-hosting.md) · [firebase-backend.md](docs/setup/firebase-backend.md)

## Product modules (API)

| Module | Entry points |
|--------|----------------|
| Discharge med rec (MVP) | `POST /api/v1/meddocs/cases`, reconcile, per-item review, finalize |
| Copilot | `POST /api/v1/copilot/chat` |
| Search | `GET /api/v1/search` |
| Meetings / Research / Workflows | `/api/v1/meetings/*`, `/research/*`, `/workflows/*` |
| Platform status | `GET /api/v1/platform/capabilities`, `/demo-readiness` |
| SMART | `GET /api/v1/smart/configuration`, `/smart/launch` |

Workbench UI: **`/dashboard`**. SMART: **`/smart/launch`**.

## Production verification

```bash
API_BASE_URL=https://YOUR_CLOUD_RUN_URL ./scripts/smoke-api.sh
API_BASE_URL=https://YOUR_CLOUD_RUN_URL ./scripts/verify-platform.sh --probe
```

Hosted E2E: `cd frontend && npm run test:e2e:deployed` (after deploy).

## Security

- No secrets in Git; Gitleaks in CI.
- Gemini key on Cloud Run via Secret Manager.
- [Security defaults](docs/security-defaults.md) — auth off by default for demos.

## License

[MIT](LICENSE)
