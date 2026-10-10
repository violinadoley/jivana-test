# MCP and tooling catalogue

Developer integrations for this monorepo: **Model Context Protocol (MCP) servers**, official CLIs/SDKs, and when to prefer each. Runtime product behavior uses **application code and GitHub Actions**, not MCP.

**Project baseline (already documented):** servers in [`.cursor/mcp.json`](../../.cursor/mcp.json) and setup steps in [docs/mcp.md](../mcp.md). This catalogue adds adoption tiers, competition-adjacent Google services, and security guidance—without duplicating full install prose from `docs/mcp.md`.

**Sources (primary):** [Google Cloud supported MCP products](https://docs.cloud.google.com/mcp/supported-products), [Google Cloud MCP overview](https://docs.cloud.google.com/mcp/overview), [Google/mcp](https://github.com/Google/mcp), vendor docs linked per entry.

**Adoption legend:** **Use now** · **Optional later** · **Investigate further** · **Avoid**

---

## Adoption tiers

### Core candidates (immediate value for this repo)

| Tool | MCP? | In `.cursor/mcp.json`? | Recommendation |
|------|------|------------------------|----------------|
| GitHub | Official ([github-mcp-server](https://github.com/github/github-mcp-server)) | Yes | **Use now** — PRs, CI, repo state |
| Context7 | Official vendor ([Upstash](https://context7.com/docs/clients/cli)) | Yes | **Use now** — library docs |
| Playwright | Official ([Microsoft](https://playwright.dev/docs/getting-started-mcp)) | Yes | **Use now** — UI verification |

### Conditional candidates (enable when workflow requires)

| Tool | MCP? | In repo config? | Recommendation |
|------|------|-----------------|----------------|
| GCP Resource Manager | Official remote | Yes | **Optional later** — confirm project |
| GCP Cloud Run | Official remote | Yes | **Optional later** — inspect/deploy (approve writes) |
| GCP Cloud Storage | Official remote | Yes | **Optional later** — debug uploads |
| GCP Firestore | Official remote | Yes | **Optional later** — inspect data (prefer dev project) |
| Firebase (`firebase-tools mcp`) | Official | Yes | **Optional later** — Hosting/rules/Auth helpers |
| Postman | Official remote | Yes | **Optional later** — HTTP API tests |
| Sentry | Official remote | Yes | **Optional later** — only if Sentry project exists |
| BigQuery | Official remote | Conditional example | **Optional later** — analytics category |
| Pub/Sub | Official remote | No | **Optional later** — async pipelines |
| Vertex AI / Agent Platform | Official remote (`aiplatform.googleapis.com/mcp/*`) | No | **Optional later** — Vertex product path |
| Agent Search | Official remote (`discoveryengine.googleapis.com/mcp`) | No | **Optional later** — managed search |
| Cloud Logging / Error Reporting | Official remote | No | **Optional later** — GCP-native triage |
| PostHog | Official ([PostHog MCP](https://posthog.com/docs/model-context-protocol)) | No | **Optional later** — flags/insights from IDE |
| Developer Knowledge API | Official remote | No | **Investigate further** — Google doc lookup vs Context7 |

### Avoid for now

| Pattern | Why |
|---------|-----|
| Enabling all GCP MCP endpoints “just in case” | Over-privilege, noise, cost |
| Unmaintained community “Google” MCP wrappers | Supply-chain risk |
| IAM MCP for routine feature work | Use docs + `gcloud` with approval |
| Duplicate Firestore access (Firebase + remote Firestore) without reason | Pick one workflow |
| MCP for languages already in repo (ESLint via MCP, etc.) | Use npm/pip scripts in CI |

---

## When MCP vs CLI vs SDK

| Need | Prefer |
|------|--------|
| Library API syntax (Next, FastAPI, GenAI SDK) | **Context7** or read repo; **SDK in code** for runtime |
| PR / branch / Actions status | **GitHub MCP** or `gh` CLI |
| Local/dashboard UI check | **Playwright MCP** or `npm run test:e2e` |
| Production API behavior | **pytest**, **Playwright CI**, **Postman** collections |
| Document AI, Vision, STT, Translation at runtime | **Google Cloud client libraries** in FastAPI |
| Deploy to Cloud Run / Hosting | **GitHub Actions** (`deploy.yml`, `deploy-frontend.yml`); Cloud Run MCP only for debug with approval |
| BigQuery / Pub/Sub jobs | **SDK + IAM**; MCP for exploratory queries in dev |

---

## Core development and repository

### GitHub

| Field | Detail |
|-------|--------|
| **MCP** | Official — `ghcr.io/github/github-mcp-server` (stdio via Docker) |
| **Docs** | [Install in Cursor](https://github.com/github/github-mcp-server/blob/main/docs/installation-guides/install-cursor.md) |
| **Auth** | OAuth (recommended); PAT only via remote example, never committed |
| **Capabilities** | Repos, issues, PRs, checks (read/write varies by tool) |
| **Cursor** | Supported via Docker stdio |
| **Risk** | Write tools can merge/close; require approval |
| **Recommendation** | **Use now** |

### Git

| Field | Detail |
|-------|--------|
| **MCP** | No official Git MCP required |
| **Prefer** | Shell git, GitHub MCP for remote state |
| **Recommendation** | **Avoid** separate Git MCP |

### GitHub Actions

| Field | Detail |
|-------|--------|
| **MCP** | Via GitHub MCP (workflow runs) |
| **Prefer** | `.github/workflows/`, Actions UI, `gh run watch` |
| **Recommendation** | **Use now** (GitHub MCP or CLI) |

### Docker

| Field | Detail |
|-------|--------|
| **MCP** | No standard official Docker MCP in this project |
| **Prefer** | `docker compose`, `backend/Dockerfile`, CI build |
| **Recommendation** | **Avoid** Docker MCP unless verified need |

### Python / pip / Ruff / mypy / pytest

| Field | Detail |
|-------|--------|
| **MCP** | None official |
| **Prefer** | `requirements*.txt`, CI in `ci.yml` |
| **Recommendation** | **Use now** (CLI/CI, not MCP) |

### Node.js / npm / ESLint / TypeScript

| Field | Detail |
|-------|--------|
| **MCP** | None official |
| **Prefer** | `frontend/package.json` scripts, CI |
| **Recommendation** | **Use now** (CLI/CI) |

### Next.js / React / Tailwind / shadcn/ui

| Field | Detail |
|-------|--------|
| **MCP** | None required |
| **Doc MCP** | **Context7** |
| **Recommendation** | **Use now** Context7 when unsure |

### Playwright

| Field | Detail |
|-------|--------|
| **MCP** | Official `@playwright/mcp` |
| **Auth** | None |
| **Capabilities** | Browser navigate, interact, snapshot |
| **Risk** | Can drive real URLs; avoid production PII |
| **Recommendation** | **Use now** |

### Context7

| Field | Detail |
|-------|--------|
| **MCP** | Official `@upstash/context7-mcp` |
| **Auth** | Optional `CONTEXT7_API_KEY` via `${env:…}` |
| **Capabilities** | Read-only documentation lookup |
| **Recommendation** | **Use now** |

---

## Google AI and Google Cloud

### Gemini API / Google AI Studio

| Field | Detail |
|-------|--------|
| **Runtime** | `google-genai` + `GEMINI_API_KEY` in backend (**Verified**) |
| **MCP** | No separate “AI Studio MCP” for app runtime |
| **Doc lookup** | Context7, [Gemini API docs](https://ai.google.dev/) |
| **Recommendation** | **SDK in app**; Context7 for agents |

### Vertex AI / Gemini on Vertex AI

| Field | Detail |
|-------|--------|
| **MCP** | Official — **Gemini Enterprise Agent Platform** endpoints, e.g. `https://aiplatform.googleapis.com/mcp/generate`, `/predict`, `/models`, `/retrieval`, `/evaluation`, `/prompts` (regional variants exist) |
| **Docs** | [Supported products](https://docs.cloud.google.com/mcp/supported-products), [MCP reference](https://docs.cloud.google.com/gemini-enterprise-agent-platform/reference/mcp) |
| **Auth** | Google OAuth / ADC; IAM e.g. `roles/mcp.toolUser` + Vertex roles |
| **Capabilities** | Model listing, generation, endpoints, RAG-related toolsets (tool-specific) |
| **App status** | **Absent** — starter uses API key path |
| **Recommendation** | **Optional later** when product requires Vertex; implement via **Vertex SDK** in FastAPI for runtime, MCP for exploration |

### Vertex AI embeddings / RAG data

| Field | Detail |
|-------|--------|
| **MCP** | Part of Agent Platform `/retrieval`, `/ragdata` toolsets (see Google docs) |
| **Runtime** | Vertex SDK or GenAI embed API |
| **Recommendation** | **Optional later** |

### Vertex AI Search / Agent Search

| Field | Detail |
|-------|--------|
| **MCP** | Official — `https://discoveryengine.googleapis.com/mcp` (**Agent Search** in supported products) |
| **Auth** | Google OAuth / IAM |
| **Runtime** | Discovery Engine / Agent Builder APIs |
| **Recommendation** | **Optional later** for managed search products |

### Vertex AI Agent Engine

| Field | Detail |
|-------|--------|
| **MCP** | No dedicated “Agent Engine only” entry; related tooling under Agent Platform / Google Cloud docs |
| **Runtime** | Agent Engine API / ADK |
| **Recommendation** | **Investigate further** — prefer ADK docs + SDK before MCP |

### Google ADK

| Field | Detail |
|-------|--------|
| **MCP** | **No official ADK MCP** listed in Google supported products |
| **Prefer** | ADK Python/JS SDK, Context7, Developer Knowledge MCP |
| **Recommendation** | **SDK**, not MCP |

### Document AI

| Field | Detail |
|-------|--------|
| **MCP** | **No official remote MCP** in [supported products](https://docs.cloud.google.com/mcp/supported-products) table |
| **Prefer** | `google-cloud-documentai` in backend |
| **Recommendation** | **SDK**; **Avoid** unverified community MCPs |

### Vision AI

| Field | Detail |
|-------|--------|
| **MCP** | **No dedicated Vision MCP** in supported products list |
| **Prefer** | Vision API client library or Gemini multimodal |
| **Recommendation** | **SDK** |

### Imagen / Veo (Genmedia)

| Field | Detail |
|-------|--------|
| **MCP** | Google [open-source/local MCP listings](https://github.com/Google/mcp) mention **Genmedia** (Imagen/Veo) — not in project `.cursor/mcp.json` |
| **Runtime** | Vertex/API SDK |
| **Recommendation** | **Investigate further** before any local Genmedia MCP; **SDK for product** |

### Speech-to-Text / Text-to-Speech / Cloud Translation

| Field | Detail |
|-------|--------|
| **MCP** | **No official STT/TTS/Translation MCP** in supported products table |
| **Prefer** | Cloud Speech/TTS/Translation client libraries |
| **Recommendation** | **SDK** |

### BigQuery / BigQuery AI

| Field | Detail |
|-------|--------|
| **MCP** | Official — `https://bigquery.googleapis.com/mcp` |
| **Config** | [`.cursor/mcp.conditional.example.json`](../../.cursor/mcp.conditional.example.json) |
| **Auth** | Google OAuth; IAM (dataset-scoped least privilege) |
| **Capabilities** | Query jobs, metadata (tool-specific; may write) |
| **Recommendation** | **Optional later** |

### Cloud SQL / AlloyDB

| Field | Detail |
|-------|--------|
| **MCP** | Official — `https://sqladmin.googleapis.com/mcp`, AlloyDB `https://alloydb.googleapis.com/mcp` |
| **Auth** | Google OAuth / IAM |
| **Recommendation** | **Optional later** if relational DB added |

### Firestore

| Field | Detail |
|-------|--------|
| **MCP** | Official remote — `https://firestore.googleapis.com/mcp`; overlap with **Firebase MCP** |
| **Auth** | OAuth; can read/write/delete documents |
| **Recommendation** | **Optional later** — dev project only; approve deletes |

### Cloud Storage

| Field | Detail |
|-------|--------|
| **MCP** | Official — `https://storage.googleapis.com/storage/mcp` |
| **In repo** | Yes |
| **Risk** | `write_text`, `delete_object` — production sensitive |
| **Recommendation** | **Optional later** |

### Cloud Run

| Field | Detail |
|-------|--------|
| **MCP** | Official — `https://run.googleapis.com/mcp` |
| **In repo** | Yes |
| **Risk** | Deploy and traffic tools — require approval |
| **Recommendation** | **Optional later** |

### Pub/Sub

| Field | Detail |
|-------|--------|
| **MCP** | Official — `https://pubsub.googleapis.com/mcp` |
| **Recommendation** | **Optional later** |

### Dataflow

| Field | Detail |
|-------|--------|
| **MCP** | **Not listed** as standalone in supported products snapshot |
| **Prefer** | Dataflow API, templates, Dataform MCP for related analytics |
| **Recommendation** | **SDK / console**; **Investigate further** for MCP |

### Earth Engine

| Field | Detail |
|-------|--------|
| **MCP** | **No official Earth Engine MCP** in supported products table |
| **Prefer** | Earth Engine Python API |
| **Recommendation** | **SDK** |

### Looker

| Field | Detail |
|-------|--------|
| **MCP** | **No official Looker MCP** in supported products table |
| **Prefer** | Looker API, embed, or in-app charts |
| **Recommendation** | **SDK/API** |

### Secret Manager

| Field | Detail |
|-------|--------|
| **MCP** | Not required for hackathon; secrets wired in **deploy.yml** |
| **Prefer** | `gcloud secrets`, GCP console |
| **Recommendation** | **Avoid MCP** for routine work |

### Cloud Logging / Monitoring / Error Reporting

| Field | Detail |
|-------|--------|
| **MCP** | Official — `https://logging.googleapis.com/mcp`, `https://monitoring.googleapis.com/mcp`, `https://clouderrorreporting.googleapis.com/mcp` |
| **Recommendation** | **Optional later** for ops debugging |

### IAM / Workload Identity Federation

| Field | Detail |
|-------|--------|
| **MCP** | Official IAM — `https://iam.googleapis.com/mcp` |
| **WIF** | Configured in repo docs, not MCP |
| **Risk** | IAM MCP can change permissions |
| **Recommendation** | **Avoid** unless explicit IAM debugging; human approval |

### Firebase Auth / Hosting / Storage

| Field | Detail |
|-------|--------|
| **MCP** | Official — `npx firebase-tools@latest mcp` |
| **Docs** | [Firebase MCP server](https://firebase.google.com/docs/ai-assistance/mcp-server) |
| **Auth** | Firebase CLI login / ADC |
| **Recommendation** | **Optional later** — prefer for hackathon Firebase workflow |

### Resource Manager

| Field | Detail |
|-------|--------|
| **MCP** | Official — `https://cloudresourcemanager.googleapis.com/mcp` |
| **In repo** | Yes |
| **Recommendation** | **Optional later** |

### Maps (Grounding Lite / Code Assist)

| Field | Detail |
|-------|--------|
| **MCP** | Official — `https://mapstools.googleapis.com/mcp`, `https://mapscodeassist.googleapis.com/mcp` |
| **Config** | Conditional example |
| **Recommendation** | **Optional later** — location-heavy products only |

### Google Analytics Data

| Field | Detail |
|-------|--------|
| **MCP** | Official — `https://analyticsdata.googleapis.com/mcp/v1` |
| **Recommendation** | **Optional later** if GA4 used (PostHog already optional in app) |

### Developer Knowledge API

| Field | Detail |
|-------|--------|
| **MCP** | Official — `https://developerknowledge.googleapis.com/mcp` |
| **Purpose** | Google developer documentation lookup |
| **Recommendation** | **Investigate further** vs Context7 for Google-only work |

### Cloud Healthcare API (FHIR / DICOM / HL7v2)

| Field | Detail |
|-------|--------|
| **Docs** | [docs.cloud.google.com/healthcare-api/docs](https://docs.cloud.google.com/healthcare-api/docs) |
| **MCP** | **No official Healthcare API MCP** in [supported products](https://docs.cloud.google.com/mcp/supported-products) |
| **Runtime** | `google-cloud-healthcare` or REST from **FastAPI** (backend only); see [healthcare-google-cloud.md](./healthcare-google-cloud.md) |
| **Doc lookup** | Context7, Developer Knowledge MCP, official docs |
| **Recommendation** | **SDK in app** when architecture approved; **Optional later** for MCP |

---

## Observability, analytics, and product development

### PostHog

| Field | Detail |
|-------|--------|
| **App** | Optional frontend SDK (**Partial**) — `frontend/lib/posthog/` |
| **MCP** | Official — `https://mcp.posthog.com/mcp` (OAuth or Bearer API key, not committed) |
| **Docs** | [PostHog MCP](https://posthog.com/docs/model-context-protocol), [Cursor setup](https://posthog.com/docs/model-context-protocol/cursor) |
| **Capabilities** | Flags, insights, errors, HogQL (many write tools) |
| **Risk** | Prompt injection; scope with `readonly=true` or tool filters when available |
| **Recommendation** | **Optional later** for IDE analytics; app SDK separate |

### Sentry

| Field | Detail |
|-------|--------|
| **App SDK** | **Absent** |
| **MCP** | Official — `https://mcp.sentry.dev/mcp` (in `.cursor/mcp.json`) |
| **Auth** | OAuth |
| **Recommendation** | **Optional later** — add SDK first if production errors matter |

### Google Analytics

| Field | Detail |
|-------|--------|
| **MCP** | Analytics Data MCP (see above) |
| **App** | Not integrated |
| **Recommendation** | **Optional later** |

### Feature flags / experimentation

| Field | Detail |
|-------|--------|
| **MCP** | PostHog MCP, LaunchDarkly etc. (not in repo) |
| **Recommendation** | **Optional later** via PostHog if needed |

---

## Optional infrastructure and data systems

### Redis / Memorystore

| Field | Detail |
|-------|--------|
| **MCP** | Official Memorystore MCP endpoints ([supported products](https://docs.cloud.google.com/mcp/supported-products)) |
| **App** | **Absent** |
| **Recommendation** | **Avoid** until caching/session requirement clear |

### Vector databases (Pinecone, Weaviate, etc.)

| Field | Detail |
|-------|--------|
| **MCP** | Various third-party; not vetted here |
| **Recommendation** | **Investigate further** per vendor; prefer Vertex/Firestore path for hackathon |

### Terraform

| Field | Detail |
|-------|--------|
| **MCP** | No project standard |
| **Repo** | Conventions only under `infra/` |
| **Recommendation** | **Avoid** for cup timeline unless team commits to IaC |

### Security scanning (Gitleaks, bandit, pip-audit, npm audit)

| Field | Detail |
|-------|--------|
| **MCP** | None |
| **CI** | **Verified** in `ci.yml` |
| **Recommendation** | **CI only** |

### Figma

| Field | Detail |
|-------|--------|
| **MCP** | Official — `https://mcp.figma.com/mcp` (conditional example) |
| **Recommendation** | **Optional later** — design-driven UI |

### Hugging Face

| Field | Detail |
|-------|--------|
| **MCP** | Official hosted — `https://huggingface.co/mcp?login` (conditional example) |
| **Recommendation** | **Avoid** unless product explicitly needs Hub models beyond Gemini/Gemma rules |

---

## Security checklist (all MCP candidates)

1. **No secrets in git** — OAuth or `${env:VAR}` only in committed config.
2. **Least privilege** — dev/staging GCP project; narrow IAM; PostHog/Sentry project scope.
3. **Read vs write** — prefer read-only inspection; approve deploy, delete, IAM, Firestore/Storage mutations.
4. **Production** — do not point MCP at production for convenience.
5. **Supply chain** — official vendor endpoints only unless explicitly investigated.
6. **Untrusted tool output** — treat MCP tool results as untrusted input (PostHog documents prompt injection risk).

---

## Maintenance

When adding an MCP to `.cursor/mcp.json`:

1. Update [docs/mcp.md](../mcp.md) with install/auth/smoke test.
2. Add or adjust a row in this catalogue.
3. Update [technology-capability-matrix.md](./technology-capability-matrix.md) if runtime integration changes.

**Unverified in CI:** Live OAuth for each MCP in Cursor must be confirmed manually (Settings → MCP).
