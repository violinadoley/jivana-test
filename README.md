# PROJECT_NAME

**Starter release:** [v1.0.0](https://github.com/violinadoley/project/releases/tag/v1.0.0) — platform complete; customize below for your competition entry.

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

Medication lists often differ across discharge paperwork, prior records, and current prescriptions. Teams need auditable evidence for each extracted field before a human reconciler can safely review changes — without auto-approving regimens from a hackathon demo.

## Solution

**MedDocs Module 1** (synthetic documents only): upload up to three files → optional Document AI OCR (or Vertex-only path when the processor is unset) → server-owned `SourceBlock` catalogs → Vertex Gemini extraction citing block IDs only → deterministic medication comparison → **`needs_review`** for every discrepancy (including documented changes) and whenever reconciliation relied on `vertex_only`/`low` evidence. Generic Gemini chat remains on `POST /api/v1/ai/generate`.

Setup: [docs/setup/document-ai-vertex-meddocs.md](docs/setup/document-ai-vertex-meddocs.md).

## Key Features

- MedDocs medication reconciliation UI (synthetic PDFs/text, review queue, evidence snippets)
- Landing page and generic AI dashboard (text + file upload)
- Gemini integration via official `google-genai` SDK (model from env)
- Firebase Auth (Google), Firestore activity feed, and GCS uploads via the API
- Optional auth (`AUTH_REQUIRED=false` for local dev)
- Structured API errors and JSON logging for Cloud Run
- Backend pytest suite and GitHub Actions CI

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
uvicorn app.main:app --reload --port 8000
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
scripts/           dev.sh, deploy.sh, smoke-api.sh
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
