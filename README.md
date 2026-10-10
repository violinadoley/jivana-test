# JIVANA

**AI Builder Cup 2026 · Future of Work & Enterprise Productivity · Healthcare**

JIVANA is an AI-powered workspace that transforms how healthcare teams **access knowledge**, **collaborate**, **make decisions**, and **complete everyday work**—with Document AI med reconciliation, enterprise search, copilot, meeting intelligence, research, and agentic workflows on **Google Cloud**.

| Doc | Purpose |
|-----|---------|
| [Design & how it works](docs/product/jivana-design-and-operations.md) | Architecture, flows, demo script, GCP mapping |
| [Roadmap / judge demo](docs/product/jivana-roadmap.md) | Competition alignment checklist |
| [MedDocs setup](docs/setup/document-ai-vertex-meddocs.md) | Document AI + Vertex med rec |

**Starter release:** [v1.0.0](https://github.com/violinadoley/JIVANA/releases/tag/v1.0.0).

| | |
|---|---|
| **Live app** | [Open dashboard](https://project-bf77a013-c0b3-413c-a75.web.app/dashboard) |
| **API (Swagger)** | Set `BACKEND_API_URL` in GitHub Variables (updated each Deploy API) or use your Cloud Run `/docs` URL |
| **Starter guide** | [docs/starter-template.md](docs/starter-template.md) |
| **Architecture decisions** | [docs/architecture/technology-decision-process.md](docs/architecture/technology-decision-process.md) |

Replace `PROJECT_NAME` and URLs when you fork for your own GCP project. Setup: [firebase-hosting.md](docs/setup/firebase-hosting.md).

## Overview

Production-quality **starter monorepo** for a Google-native AI hackathon project. It includes a Next.js dashboard, FastAPI backend with Gemini, Firebase-ready auth/data/storage hooks, Docker for Cloud Run, tests, and CI.

Replace placeholders (`PROJECT_NAME`, problem statement, domain logic) after your team selects a competition track.

**GitHub Actions variables** (see [docs/security-defaults.md](docs/security-defaults.md)):

| Variable | Purpose |
|----------|---------|
| `PUBLIC_API_URL` | Cloud Run **base URL** (no `/docs`) — baked into the frontend as `NEXT_PUBLIC_API_URL` |
| `BACKEND_API_URL` | **Swagger** URL (`…/docs`) — updated after Deploy API for humans / README links |

Local API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## Problem

Healthcare teams lose productivity when knowledge is scattered across policies, meetings, and documents—and when medication lists disagree at care transitions without auditable review.

## Solution (workspace modules)

| Module | API |
|--------|-----|
| Copilot | `POST /api/v1/copilot/chat` |
| Intelligent search | `GET /api/v1/search` |
| **Discharge med rec workbench (MVP)** | `POST /api/v1/meddocs/cases`, `…/reconcile`, `PATCH …/items/{item_id}`, `…/finalize-review` |
| Document intelligence (legacy one-shot) | `POST /api/v1/meddocs/reconciliation` |
| Meeting intelligence | `POST /api/v1/meetings/intelligence` |
| Research | `POST /api/v1/research/synthesize` |
| Workflow agent | `POST /api/v1/workflows/agent-run` |
| Platform status | `GET /api/v1/platform/capabilities` |

Open **`/dashboard`**. For the hackathon MVP, set **`NEXT_PUBLIC_MVP_WORKBENCH=true`** in `frontend/.env.local` (see `.env.local.example`) for the case-centric discharge workbench. Enterprise tabs remain in code behind that flag. Setup: [document-ai-vertex-meddocs.md](docs/setup/document-ai-vertex-meddocs.md), [vertex-ai-search-bigquery.md](docs/setup/vertex-ai-search-bigquery.md).

## Key Features

- Discharge medication reconciliation workbench (per-item review, finalize attestation, HTML summary)
- Optional eight-tab enterprise workspace (hidden when `NEXT_PUBLIC_MVP_WORKBENCH=true`)
- Gemini on Vertex AI (Cloud Run) + optional Vertex AI Search, Document AI, Healthcare FHIR, BigQuery events
- Firebase Auth, Firestore activity/sessions, GCS uploads
- pytest + Playwright smoke + GitHub Actions CI/deploy

## Tech Stack

| Layer | Technologies |
|-------|----------------|
| Frontend | Next.js, React, TypeScript, Tailwind CSS, shadcn/ui, Lucide |
| Backend | Python 3.11+, FastAPI, Uvicorn, Pydantic Settings |
| AI | Google Gemini (`google-genai`) |
| Data / Auth | Firebase (Auth, Firestore, Storage) |
| Deploy | Cloud Run (API), Firebase Hosting (UI, static export) |

## Architecture

See [docs/architecture.md](docs/architecture.md) for diagrams and extension points (RAG, ADK, embeddings — **future**).

## Local Setup

```bash
git clone <your-repo-url>
cd ai-hackathon-starter
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local
# Add GEMINI_API_KEY to backend/.env
```

Or run `./scripts/dev.sh` for instructions.

## Environment Variables

**Backend** (`backend/.env`): `GEMINI_API_KEY`, `GEMINI_MODEL`, `FIREBASE_PROJECT_ID`, `FIREBASE_STORAGE_BUCKET`, `AUTH_REQUIRED`, `MAX_UPLOAD_SIZE_MB`, `CORS_ORIGINS`, etc. See [backend/.env.example](backend/.env.example).

**Frontend** (`frontend/.env.local`): `NEXT_PUBLIC_API_URL` (same meaning as `PUBLIC_API_URL`), `NEXT_PUBLIC_FIREBASE_*`, `NEXT_PUBLIC_AUTH_REQUIRED`. See [frontend/.env.local.example](frontend/.env.local.example).

Security defaults (auth, public API, CI gates): [docs/security-defaults.md](docs/security-defaults.md).

Optional product analytics (PostHog): [docs/setup/posthog.md](docs/setup/posthog.md).

## Running Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Running Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --reload-dir app --port 8000
```

Health check: [http://localhost:8000/health](http://localhost:8000/health)

## Testing

See [docs/development/testing-strategy.md](docs/development/testing-strategy.md).

```bash
cd backend && pip install -r requirements-dev.txt
ruff check app tests && mypy app && pytest -q
PYTHONPATH=. pytest ../ai-evals/regression -q

cd frontend && npm ci
npm run lint && npm run typecheck && npm run build
npm run test:e2e
```

## Git workflow

- Feature branches merge into `develop` via PR; **`develop`** triggers Cloud Run deploy
- **`main`** is the stable branch (no separate prod deploy in this hackathon setup)
- See [CONTRIBUTING.md](CONTRIBUTING.md)

## CI/CD

| Workflow | Trigger | Status |
|----------|---------|--------|
| [ci.yml](.github/workflows/ci.yml) | PR + push to `main` / `develop` | **AUTOMATED** (in repo) |
| [deploy.yml](.github/workflows/deploy.yml) | push to `develop` | Cloud Run API |
| [deploy-frontend.yml](.github/workflows/deploy-frontend.yml) | push to `develop` | Firebase Hosting (free) |

Setup: [docs/setup/github-google-oidc.md](docs/setup/github-google-oidc.md) · [docs/setup/firebase-hosting.md](docs/setup/firebase-hosting.md) · [docs/setup/firebase-backend.md](docs/setup/firebase-backend.md)

## Deployment

- Overview: [docs/deployment.md](docs/deployment.md)
- Cloud Run: [docs/deployment/cloud-run.md](docs/deployment/cloud-run.md)
- Rollback: [docs/runbooks/rollback.md](docs/runbooks/rollback.md)
- Post-deploy checks: [docs/setup/verify-integrations.md](docs/setup/verify-integrations.md) (`./scripts/smoke-api.sh`, `./scripts/verify-platform.sh`)

## Google Cloud Setup

1. Create a GCP project and enable Cloud Run, Cloud Build, Secret Manager.
2. Store `GEMINI_API_KEY` in Secret Manager.
3. Deploy the backend from `./backend` (Dockerfile included).

## Firebase Setup

1. Add Firebase to the same GCP project as Cloud Run.
2. Follow [docs/setup/firebase-hosting.md](docs/setup/firebase-hosting.md) (public UI) and [docs/setup/firebase-backend.md](docs/setup/firebase-backend.md) (Auth, Firestore, Storage, GitHub vars).
3. Sync web client vars: `./scripts/sync-firebase-github-vars.sh YOUR_GCP_PROJECT_ID` (after `firebase login` and a registered Web app).

## Gemini Setup

1. Get an API key from [Google AI Studio](https://aistudio.google.com/apikey).
2. Set `GEMINI_API_KEY` and optionally `GEMINI_MODEL` (default `gemini-2.5-flash`).

## Project Structure

```
frontend/          Next.js App Router UI
backend/app/       FastAPI application
backend/tests/     Pytest suite
docs/              Architecture, ADRs, runbooks, deployment, security
ai-evals/          AI regression framework (datasets + evaluators)
infra/             Infra conventions (no Terraform by default)
scripts/           dev.sh, deploy.sh, smoke-api.sh, verify-platform.sh
.github/workflows/ CI + Cloud Run deploy
```

## Starter template status

The **platform starter** (CI/CD, Hosting, Cloud Run, Auth, activity in Firestore, uploads to Storage) is complete on `develop`. See [docs/starter-template.md](docs/starter-template.md). Build your competition on top via prompts, routes, and UI — [docs/architecture.md](docs/architecture.md).

## Future Enhancements (product team)

- [ ] Competition-specific prompts and workflows
- [ ] Richer chat history and user-scoped activity
- [ ] RAG + Gemini embeddings + vector search
- [ ] Google ADK agentic tools
- [ ] Structured outputs and multimodal pipelines

## Competition Submission Checklist

- [ ] Correct problem statement selected
- [ ] Gemini/Gemma integration
- [ ] Functional prototype
- [ ] Cloud deployment
- [ ] Public demo URL
- [ ] 3-minute demo video
- [ ] Proposal PDF
- [ ] Documentation
- [ ] Category specified
- [ ] Impact clearly explained
- [ ] Scalability explained

## Optional (local dev only)

IDE MCP helpers for this repo: [docs/mcp.md](docs/mcp.md) — not part of the deployed product.

## License

[MIT](LICENSE) — adjust copyright holder if your team requires a different license for submission.
