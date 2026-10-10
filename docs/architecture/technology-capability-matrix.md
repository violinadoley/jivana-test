# Technology capability matrix

Reference for **AI Builder Cup 2026** technical decisions on top of this starter. The team chooses the product idea; this document does not recommend a competition concept.

**Status legend**

| Status | Meaning |
|--------|---------|
| **Verified** | Implemented in repo; exercised in CI and/or deploy path |
| **Unverified** | Present in repo; not re-validated in a specific environment |
| **Partial** | Implemented but env-gated, stubbed, or optional |
| **Planned** | Documented extension point or `NotImplementedError` stub |
| **Optional** | Supported when keys/config are set |
| **Absent** | Not in application code or deploy wiring |

**Related:** [technology-decision-process.md](./technology-decision-process.md) · [mcp-and-tooling-catalogue.md](./mcp-and-tooling-catalogue.md) · [healthcare-google-cloud.md](./healthcare-google-cloud.md) · [docs/architecture.md](../architecture.md)

**Team direction:** healthcare — primary clinical platform reference: [Cloud Healthcare API docs](https://docs.cloud.google.com/healthcare-api/docs).

---

## 1. Frontend and UI

| Technology | Purpose | Starter status | Cup relevance | Alternatives | Setup | Complexity | Cost | Adopt when | Avoid when |
|------------|---------|----------------|---------------|--------------|-------|------------|------|------------|------------|
| **Next.js (App Router)** | SSR/static export, routing, dashboard | **Verified** | All categories | Remix, Vite SPA | `frontend/`, Node 20+ | Low | Hosting free tier | Default UI | Replacing entire frontend mid-hackathon |
| **React + TypeScript** | Components, type safety | **Verified** | All | Vue, Svelte | `frontend/` | Low | — | Default | — |
| **Tailwind CSS** | Styling | **Verified** | All | CSS modules only | `frontend/` | Low | — | Default | Second CSS framework |
| **shadcn/ui** | Accessible UI primitives | **Verified** | All | MUI, Chakra | `frontend/components/ui` | Low | — | Dashboard/forms | Heavy custom design system |
| **Lucide** | Icons | **Verified** | All | Heroicons | npm dep | Low | — | Icons needed | — |
| **Static export + Firebase Hosting** | Public demo URL | **Verified** | Submission | Vercel-only | `deploy-frontend.yml` | Medium | Spark free tier | Hackathon deploy | Need SSR on every request |

---

## 2. Backend and APIs

| Technology | Purpose | Starter status | Cup relevance | Alternatives | Setup | Complexity | Cost | Adopt when | Avoid when |
|------------|---------|----------------|---------------|--------------|-------|------------|------|------------|------------|
| **FastAPI** | HTTP API, OpenAPI | **Verified** | All | Flask, Cloud Functions only | `backend/app/` | Low | Cloud Run usage | Default API | Splitting into many microservices |
| **Uvicorn** | ASGI server | **Verified** | All | Hypercorn | local + Docker | Low | — | Default | — |
| **Pydantic Settings** | Config from env | **Verified** | All | os.environ ad hoc | `backend/app/core/config.py` | Low | — | All env config | — |
| **Structured errors + JSON logging** | Ops/debug | **Verified** | All | Plain text logs | `exceptions.py`, `logging.py` | Low | Logging volume | Production API | — |
| **python-multipart** | File uploads | **Verified** | Media, docs | Signed URL-only | file routes | Low | — | Upload endpoints | — |

---

## 3. General-purpose AI and reasoning

| Technology | Purpose | Starter status | Cup relevance | Alternatives | Setup | Complexity | Cost | Adopt when | Avoid when |
|------------|---------|----------------|---------------|--------------|-------|------------|------|------------|------------|
| **Gemini API + `google-genai`** | Text generation via API key | **Verified** | All (Gemma/Gemini rules) | Vertex-only path | `GEMINI_API_KEY`, `GeminiService` | Low | Pay-per-token / free tier | Fast hackathon iteration, current starter | Strict enterprise Vertex-only policy |
| **Gemini on Vertex AI** | IAM, regional endpoints, enterprise features | **Absent** (app) | Cup “Vertex” mentions | Stay on Gemini API | GCP project, Vertex enable, SA/WIF | Medium–High | Vertex pricing | Need VPC-SC, fine-tuning, some judges expect Vertex | Simple demo already on API key |
| **Versioned prompts** | Reproducible AI behavior | **Verified** | All | Inline strings | `backend/app/ai/prompts/` | Low | — | Any prompt change | Unversioned prompt edits |
| **General `generate_content`** | Q&A, summarization | **Verified** | All | Specialized APIs | `POST /api/v1/ai/generate` | Low | Token cost | Primary LLM calls | Document AI for pure text |
| **Structured JSON outputs** | Machine-readable AI results | **Planned** | BFSI, retail forms | Regex parsing | Extend `GeminiService` + schema | Medium | Tokens | Forms, extraction | Over-schema everything |
| **Chat / multi-turn** | Conversational UX | **Planned** | Future of work | Stateless single shot | Firestore history + API | Medium | Storage + tokens | Chat product | Single-shot suffices |

---

## 4. Embeddings, retrieval, vector search, and RAG

| Technology | Purpose | Starter status | Cup relevance | Alternatives | Setup | Complexity | Cost | Adopt when | Avoid when |
|------------|---------|----------------|---------------|--------------|-------|------------|------|------------|------------|
| **In-app RAG (Firestore + embeddings)** | Context from own data | **Planned** | Search-heavy categories | Vertex AI Search only | Embeddings API + index | High | Storage + embed + query | Custom corpus, small scale | Managed search is enough |
| **Vertex AI embeddings** | Vector generation | **Absent** | RAG, commerce | Gemini embedding via API | Vertex or GenAI embed API | Medium | Per char/token | Semantic search | Keyword search enough |
| **Vertex AI Search / Agent Search** | Managed retrieval + agents | **Absent** | Retail, BFSI, productivity | DIY RAG | GCP console + API | Medium–High | Product pricing | Large doc sets, Google search stack | Tiny FAQ |
| **Vector DB (Pinecone, etc.)** | Dedicated vectors | **Absent** | Optional RAG | Firestore + brute force, Vertex | New service + sync | High | SaaS cost | Scale beyond Firestore | Hackathon MVP |
| **`generate_with_context` stub** | RAG hook in code | **Planned** | — | — | `GeminiService` | — | — | Implementing RAG | — |

---

## 5. Agents and workflow orchestration

| Technology | Purpose | Starter status | Cup relevance | Alternatives | Setup | Complexity | Cost | Adopt when | Avoid when |
|------------|---------|----------------|---------------|--------------|-------|------------|------|------------|------------|
| **FastAPI route orchestration** | Deterministic workflows | **Verified** | All | Full agent framework | Python code | Low | — | Most hackathon flows | — |
| **Tool calling (Gemini function calling)** | Model-driven tools | **Planned** | Productivity | ADK | Extend AI layer | Medium | Tokens | Few well-defined tools | Open-ended agent |
| **Google ADK** | Agent development kit | **Absent** | Future of work | Custom agents | New dep + GCP | High | GCP | Multi-tool agents | Single LLM call |
| **Vertex AI Agent Engine** | Hosted agents | **Absent** | Productivity | ADK + Run | GCP setup | High | GCP | Managed agent runtime | Simple pipeline |

---

## 6. Documents and structured extraction

| Technology | Purpose | Starter status | Cup relevance | Alternatives | Setup | Complexity | Cost | Adopt when | Avoid when |
|------------|---------|----------------|---------------|--------------|-------|------------|------|------------|------------|
| **PDF/image upload to GCS** | Ingest files | **Partial** | BFSI, manufacturing | Drive API | File upload route | Medium | Storage | User uploads | — |
| **Gemini multimodal (PDF/image in prompt)** | Parse docs in-model | **Planned** | BFSI, docs | Document AI | `analyze_image` / parts | Medium | Tokens | Moderate doc volume | High-volume OCR/forms |
| **Document AI** | OCR, forms, specialized parsers | **Partial** (MedDocs optional processor) | BFSI, productivity, healthcare docs | Gemini vision / Vertex-only fallback | [document-ai-vertex-meddocs.md](../setup/document-ai-vertex-meddocs.md) | Medium | Per page | MedDocs intake when processor configured | Misconfigured processor (fail fast, no silent fallback) |
| **Vertex Gemini (ADC) — MedDocs module** | Classify/extract with `source_block_id` citations | **Partial** (Module 1 prototype) | Healthcare docs | API-key Gemini route | `POST /api/v1/meddocs/*` | Medium | Token cost | Structured med reconciliation demo | Production PHI without compliance review |

---

## 7. Image, video, and audio

| Technology | Purpose | Starter status | Cup relevance | Alternatives | Setup | Complexity | Cost | Adopt when | Avoid when |
|------------|---------|----------------|---------------|--------------|-------|------------|------|------------|------------|
| **Gemini multimodal** | Image understanding | **Planned** | Manufacturing, sustainability | Vision API | Extend `GeminiService` | Medium | Tokens | Unified model path | Dedicated Vision needed |
| **Vision AI** | Labels, OCR, specialized CV | **Absent** | Manufacturing, sustainability | Gemini vision | GCP Vision API | Medium | Per unit | CV pipelines | Casual image Q&A |
| **Imagen** | Image generation | **Absent** | Media | External APIs | Vertex Imagen | Medium | Per image | Generative media | — |
| **Veo** | Video generation | **Absent** | Media | — | Vertex / Genmedia | High | High | Video gen product | — |
| **Speech-to-Text / Text-to-Speech** | Voice UX | **Absent** | Media, accessibility | Browser APIs | GCP STT/TTS | Medium | Per minute | Voice interface | Text-only |
| **Cloud Translation** | Localization | **Absent** | Media, global retail | Gemini translate | Translation API | Low–Medium | Per char | Many languages | English-only demo |

---

## 8. Databases and analytics

| Technology | Purpose | Starter status | Cup relevance | Alternatives | Setup | Complexity | Cost | Adopt when | Avoid when |
|------------|---------|----------------|---------------|--------------|-------|------------|------|------------|------------|
| **Firestore** | App state, activity feed | **Verified** (cloud) | Productivity, all | Postgres | Firebase + Admin SDK | Medium | Free tier small | User/session/activity data | **Clinical FHIR system of record** (use Healthcare API) |
| **Cloud Healthcare API (FHIR/DICOM/HL7v2)** | Standards-based clinical/imaging storage | **Absent** | **Healthcare (team)** | Firestore-as-FHIR hack | Enable `healthcare.googleapis.com`, dataset + store | Medium–High | Per API/storage | Interop, imaging, de-id pipelines | Simple non-clinical demo with no FHIR need |
| **Cloud Storage / Firebase Storage** | Blobs, uploads | **Verified** (when configured) | Retail, media | S3-compatible only | Bucket + backend | Medium | Storage + egress | Files, exports | DB for relational data |
| **BigQuery** | Analytics, large SQL | **Absent** | All categories (analytics) | Firestore export | Dataset + IAM | Medium–High | Storage + query | Dashboards on big data | OLTP app state |
| **BigQuery AI** | SQL + ML in BQ | **Absent** | Retail, BFSI | Vertex ML | BigQuery | High | BQ ML | Data already in BQ | No data warehouse |
| **Cloud SQL** | Relational OLTP | **Absent** | BFSI, retail | AlloyDB, Firestore | Instance + connector | High | Instance cost | Strong relational needs | Simple document model |
| **AlloyDB** | Postgres-compatible scale | **Absent** | BFSI, retail | Cloud SQL | Cluster | High | $$$ | Postgres at scale | Hackathon MVP |
| **Looker** | BI dashboards | **Absent** | Retail | Looker Studio, charts in app | Looker license | High | License | Enterprise BI | Demo charts in Next |

---

## 9. Predictive ML and data pipelines

| Technology | Purpose | Starter status | Cup relevance | Alternatives | Setup | Complexity | Cost | Adopt when | Avoid when |
|------------|---------|----------------|---------------|--------------|-------|------------|------|------------|------------|
| **Vertex AI training / prediction** | Custom ML models | **Absent** | Manufacturing, sustainability | BigQuery ML | Vertex pipelines | High | Compute | Real ML forecast | LLM pretends to predict |
| **BigQuery ML** | SQL-based models | **Absent** | BFSI, retail | Vertex | BQ only | Medium–High | BQ | Data in BigQuery | No warehouse |
| **Dataflow** | Stream/batch ETL | **Absent** | Manufacturing | Pub/Sub + Cloud Functions | Dataflow job | High | Worker cost | Large pipelines | Small event volume |
| **Earth Engine** | Geospatial analysis | **Absent** | Sustainability | Static maps + Gemini | EE account | High | EE terms | Geo sustainability | Non-geo problem |

---

## 10. Messaging and event-driven processing

| Technology | Purpose | Starter status | Cup relevance | Alternatives | Setup | Complexity | Cost | Adopt when | Avoid when |
|------------|---------|----------------|---------------|--------------|-------|------------|------|------------|------------|
| **Pub/Sub** | Async events | **Absent** | BFSI, manufacturing | In-process queue | Topic + subs | Medium | Message volume | Decouple services | Sync FastAPI enough |
| **Cloud Functions / Cloud Run jobs** | Event handlers | **Absent** | All async | FastAPI background | GCP deploy | Medium | Invocations | Short async tasks | Long jobs without design |
| **In-request async (`asyncio`)** | Non-blocking I/O | **Verified** | All | Celery | Gemini in thread pool | Low | — | Current API | Heavy offline jobs |

---

## 11. Cloud infrastructure and deployment

| Technology | Purpose | Starter status | Cup relevance | Alternatives | Setup | Complexity | Cost | Adopt when | Avoid when |
|------------|---------|----------------|---------------|--------------|-------|------------|------|------------|------------|
| **Cloud Run** | API hosting | **Verified** | All | GKE, Functions | `deploy.yml`, Dockerfile | Medium | Request/CPU | Default API host | k8s for hackathon |
| **Firebase Hosting** | Static frontend | **Verified** | All | Cloud CDN only | `deploy-frontend.yml` | Medium | Free tier | Public UI | SSR host |
| **Docker** | Container build | **Verified** | All | Buildpacks only | `backend/Dockerfile` | Low | Build minutes | Cloud Run path | — |
| **Artifact Registry** | Images | **Verified** (with GCP vars) | All | GCR legacy | WIF + AR | Medium | Storage | CI deploy | — |
| **Secret Manager** | Gemini key at runtime | **Verified** | All | Env only (dev) | GCP secret + deploy flag | Medium | Secret ops | Production API | Committing keys |
| **Workload Identity Federation** | Keyless GitHub → GCP | **Verified** (configured per project) | All | SA JSON in CI | OIDC doc | High one-time | — | GitHub Actions deploy | Long-lived keys in GitHub |
| **Terraform / IaC** | Repro infra | **Absent** (by design) | — | Manual + docs | `infra/` conventions | — | — | Team wants full IaC | Current hackathon scope |

---

## 12. Authentication and security

| Technology | Purpose | Starter status | Cup relevance | Alternatives | Setup | Complexity | Cost | Adopt when | Avoid when |
|------------|---------|----------------|---------------|--------------|-------|------------|------|------------|------------|
| **Firebase Authentication (Google)** | User sign-in | **Verified** | All | Custom OAuth | Web app + client env | Medium | Free tier | User-specific data | Public demo only |
| **Optional `AUTH_REQUIRED`** | Lock API | **Verified** | All | Always public | env flags | Low | — | After auth wired | Early dev |
| **Firebase Admin token verify** | Backend auth | **Verified** | All | API keys | `deps.py`, tests | Medium | — | Protected routes | — |
| **Deny-all Firestore/Storage rules** | Client cannot bypass API | **Verified** | All | Open rules | rules + CI deploy | Medium | — | Default | Direct client DB access |
| **CORS** | Browser API access | **Verified** | All | Proxy only | `CORS_ORIGINS` | Low | — | Web app | — |
| **CI: Gitleaks, bandit, pip-audit, npm audit** | Supply chain | **Verified** | All | Manual | `ci.yml` | Low | — | Every PR | Disabling checks |

---

## 13. Testing and browser automation

| Technology | Purpose | Starter status | Cup relevance | Alternatives | Setup | Complexity | Cost | Adopt when | Avoid when |
|------------|---------|----------------|---------------|--------------|-------|------------|------|------------|------------|
| **pytest** | Backend tests | **Verified** | All | unittest | `backend/tests/` | Low | CI time | All behavior changes | — |
| **Ruff + mypy** | Lint/types | **Verified** | All | flake8 | CI | Low | — | Python changes | — |
| **Playwright (CI)** | E2E smoke | **Verified** | All | Cypress | `frontend/e2e/` | Medium | CI minutes | Critical journeys | Unit-only for UI |
| **Playwright MCP** | Agent-driven browser checks | **Optional** (dev IDE) | All | Manual QA | `.cursor/mcp.json` | Low | — | Verify UI in Cursor | — |
| **ai-evals regression** | Prompt/model regression | **Verified** (framework) | All | Manual only | `ai-evals/` | Medium | — | Prompt/model changes | — |
| **ESLint + tsc** | Frontend quality | **Verified** | All | — | `npm run lint/typecheck` | Low | — | TS/React changes | — |

---

## 14. Observability and product analytics

| Technology | Purpose | Starter status | Cup relevance | Alternatives | Setup | Complexity | Cost | Adopt when | Avoid when |
|------------|---------|----------------|---------------|--------------|-------|------------|------|------------|------------|
| **Cloud Logging (Run)** | API logs | **Verified** (platform) | All | — | Cloud Run default | Low | Log volume | Production debug | — |
| **PostHog (frontend)** | Funnels, workflow analytics | **Optional** | Demo evidence | GA4 | `NEXT_PUBLIC_POSTHOG_*` | Low | Free tier | Product analytics | Logging prompts/PII |
| **Sentry (runtime SDK)** | Error tracking in app | **Absent** | All | Cloud Error Reporting | SDK + DSN | Medium | Sentry plan | Rich error UX | MCP-only triage |
| **Sentry MCP** | Investigate issues from IDE | **Optional** (dev) | All | Console only | OAuth in Cursor | Low | — | After Sentry project exists | Without Sentry project |
| **Cloud Error Reporting MCP** | GCP errors | **Absent** (config) | All | Sentry | GCP MCP enable | Medium | — | GCP-native errors | — |

---

## 15. Developer productivity and documentation

| Technology | Purpose | Starter status | Cup relevance | Alternatives | Setup | Complexity | Cost | Adopt when | Avoid when |
|------------|---------|----------------|---------------|--------------|-------|------------|------|------------|------------|
| **Cursor rules** | Persistent engineering policy | **Verified** | — | Wiki only | `.cursor/rules/` | Low | — | All agent work | — |
| **Architecture matrix + catalogue** | Tech/MCP decisions | **Verified** (this doc) | — | Ad hoc | `docs/architecture/` | Low | — | Before new services | — |
| **Context7 MCP** | Library docs lookup | **Optional** (dev) | — | Web search | `mcp.json` | Low | API key optional | Unfamiliar APIs | Known APIs |
| **docs/mcp.md** | MCP setup guide | **Verified** | — | — | repo | Low | — | IDE GCP/Firebase work | — |
| **GitHub MCP** | PRs, issues, CI | **Optional** (dev) | — | `gh` CLI | Docker OAuth | Low | — | Repo automation | — |
| **Postman MCP** | HTTP API testing | **Optional** (dev) | — | curl, pytest | OAuth | Low | — | API contract checks | — |
| **Developer Knowledge API MCP** | Google doc lookup | **Absent** (config) | Google Cloud features | Context7 | GCP MCP URL | Low | — | Heavy GCP API work | — |

---

## Quick “start here” for approved product work

1. Extend **Gemini API** flows in `backend/app/ai/` and existing routes.
2. Persist in **Firestore** / files in **GCS** via existing services.
3. Add **category-specific** GCP services only when the matrix shows a clear gap and the team approved an architecture proposal.
4. Use **MCP catalogue** for IDE assistance; use **SDKs in app code** for runtime behavior.
