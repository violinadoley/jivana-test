# JIVANA — design, implementation, and how it works today

**Theme:** Future of Work & Enterprise Productivity  
**Domain:** Healthcare operations (knowledge, collaboration, decisions, everyday work)  
**Competition fit:** AI Builder Cup 2026 — Technical Merit 40%, Problem Alignment 25%, Innovation 25%, UX 10%

---

## 1. Design intent (what we built and why)

### Problem (official framing)

Healthcare teams lose time when knowledge lives in PDFs, meetings, policies, and EHR silos. Medication reconciliation alone spans discharge summaries, pharmacy lists, and human sign-off. JIVANA is one **enterprise workspace** that unifies:

1. **Find** — intelligent search (Vertex AI Search + institutional corpus)  
2. **Understand** — copilot, research synthesis, meeting briefs  
3. **Act** — document intelligence with mandatory human review  
4. **Prove** — activity feed, productivity metrics, BigQuery events, FHIR export  

### Design principles

| Principle | Implementation |
|-----------|----------------|
| Human-in-the-loop for clinical risk | Med rec never auto-completes with weak evidence; review queue + acknowledgment |
| Server-side Gen AI only | All Gemini/Document AI on Cloud Run; browser calls FastAPI only |
| Auditable artifacts | Source blocks, activity in Firestore, optional FHIR Bundle after sign-off |
| Demo-safe | Synthetic documents; no PHI in repo or analytics payloads |
| GCP-native | Vertex Gemini ADC, Document AI, Discovery Engine, Healthcare API, BigQuery, Firestore |

### Information architecture (UI)

Single app: **Marketing home** (`/`) → **Hybrid workspace** (`/dashboard`, default):

```
Discharge med rec → case list, compare, per-item review, finalize, HTML summary
Search            → Vertex AI Search + corpus
Copilot           → multi-turn sessions (Firestore)
Meetings          → transcript → summary / decisions / actions
Research          → search-backed cited synthesis
Workflows         → multi-step agent (tools then plan)
Insights          → productivity counts + activity + med-rec metrics
```

Set `NEXT_PUBLIC_MVP_WORKBENCH=false` for the legacy eight-tab layout (Overview + Documents job queue).

---

## 2. System architecture (implementation)

```text
┌─────────────────────────────────────────────────────────────────┐
│  Next.js (Firebase Hosting)                                      │
│  Workspace tabs · JIVANA brand · Firebase Auth (optional)        │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS  /api/v1/*
┌────────────────────────────▼────────────────────────────────────┐
│  Cloud Run · FastAPI (BFF)                                         │
│  ┌─────────────┐ ┌──────────────┐ ┌─────────────────────────────┐ │
│  │ Copilot     │ │ MedDocs      │ │ Enterprise modules          │ │
│  │ sessions    │ │ pipeline     │ │ search · meetings · research│ │
│  └──────┬──────┘ └──────┬───────┘ │ workflows · analytics       │ │
│         │               │         └──────────────┬──────────────┘ │
└─────────┼───────────────┼────────────────────────┼───────────────┘
          │               │                        │
    Firestore       Document AI              Vertex AI Search
    (activity,      + Vertex Gemini          (optional)
     sessions,       + GCS uploads
     med jobs)       + FHIR export ──► Cloud Healthcare API
                                            BigQuery ◄── productivity events
```

### Request flows (today)

**Copilot chat**

1. `POST /api/v1/copilot/chat` with `message` (+ optional `session_id`).  
2. Backend loads/creates Firestore session; appends user message.  
3. Retrieves institutional excerpts + `EnterpriseSearchService.search()`.  
4. Renders `prompts/v1/copilot.txt` → **Vertex Gemini** (ADC on Cloud Run).  
5. Stores assistant reply; logs activity + optional BigQuery row.

**Enterprise search**

1. `GET /api/v1/search?q=`.  
2. If `VERTEX_SEARCH_DATA_STORE_ID` set → Discovery Engine `SearchServiceClient`.  
3. Always merges keyword hits from `app/data/institutional_knowledge.json`.  
4. Returns `engine` label (`vertex_ai_search` vs `institutional_corpus`).

**MedDocs reconciliation**

1. `POST /api/v1/meddocs/reconciliation` (1–3 files).  
2. Cloud: Document AI **required**; extracts `SourceBlock`s.  
3. Vertex Gemini structured extract per document → deterministic reconciler.  
4. Status `needs_review` or `completed` (strict evidence rules).  
5. `POST .../review` on acknowledge → `on_reconciliation_completed()` → FHIR POST if Healthcare env set.

**Workflow agent (hybrid: deterministic + ADK on Cloud Run)**

1. `POST /api/v1/workflows/agent-run`.  
2. **Steps 1–2 (always deterministic):** institutional knowledge, then enterprise search.  
3. **Step 3:** markdown plan via **Google ADK** when `AGENT_BACKEND=auto|adk`, else legacy Gemini template.  
4. Response includes `steps[]` (tool, status, preview). Copilot, research, and meetings use ADK with shared knowledge/search tools when enabled. **Med rec is never ADK-driven.**

**Analytics**

1. `GET /api/v1/analytics/productivity` — aggregates Firestore `activity` by type.  
2. Mutating routes append to BigQuery when `BIGQUERY_DATASET_ID` configured.

**Platform status**

1. `GET /api/v1/platform/capabilities` — which GCP integrations are live (env-driven).

---

## 3. Google Cloud mapping (judging: Technical Merit 40%)

| Suggested technology | Role in JIVANA | Config / proof |
|---------------------|----------------|----------------|
| Gemini on Vertex AI | Copilot, meetings, research, workflows, med extract | Cloud Run ADC, `VERTEX_LOCATION` |
| Vertex AI Search | Primary search when data store exists | `VERTEX_SEARCH_DATA_STORE_ID` |
| Document AI | OCR/layout blocks for med rec | `DOCUMENT_AI_PROCESSOR_ID` |
| Workflow agent | Multi-step orchestration on Cloud Run | **Verified**; steps visible in API and UI |
| Vertex AI Agent Engine / ADK | Optional hosted runtime | **Phase 2**; same tools, different hosting |
| Cloud Run | API host | `deploy.yml` |
| BigQuery | Productivity event stream | `BIGQUERY_DATASET_ID` |
| Firestore | Sessions, jobs, activity | `FIREBASE_PROJECT_ID` |
| Cloud Healthcare API | FHIR export after review | `HEALTHCARE_*` |
| Firebase Hosting | Static Next.js | `deploy-frontend.yml` |

---

## 4. How to demo (15 minutes — Problem Alignment + UX)

Default UI: **hybrid workspace** (`NEXT_PUBLIC_MVP_WORKBENCH` not `false`) — tab bar on `/dashboard` with **Discharge med rec** plus tools.

1. **Discharge med rec** (6–7 min) — create case → **Load synthetic demo trio** or upload prior/discharge/Rx → resolve each item → **Complete item review** (legacy cases) → **Finalize** → **Open HTML summary**.  
2. **Search** — “medication reconciliation policy”.  
3. **Meetings** — paste stand-up/handoff transcript → summary and action items.  
4. **Copilot** — follow-up using session memory.  
5. **Research** — show answer **and source list**.  
6. **Workflows** — expand agent **steps** then plan.  
7. **Insights** — activity + med-rec metrics; mention BigQuery if enabled.

Legacy eight-tab sandbox: set `NEXT_PUBLIC_MVP_WORKBENCH=false`.

---

## 5. Local vs production behavior

| Feature | Local (typical) | Cloud Run (configured) |
|---------|-----------------|-------------------------|
| Gemini | `GEMINI_API_KEY` or ADC | Vertex ADC |
| Document AI | Optional; text path if unset | Required for med rec |
| Vertex Search | Corpus only unless env set | Discovery Engine + corpus |
| FHIR | Skipped | POST to FHIR store |
| BigQuery | No-op | Streaming inserts |
| Firestore | Optional | Activity + sessions + jobs |

---

## 6. Files to know (implementation index)

| Area | Path |
|------|------|
| API router | `backend/app/api/router.py` |
| MedDocs pipeline | `backend/app/services/documents/intake_pipeline.py` |
| Search | `backend/app/services/search/enterprise_search_service.py` |
| FHIR | `backend/app/services/healthcare/fhir_export_service.py` |
| Prompts | `backend/app/ai/prompts/v1/*.txt` |
| Workspace UI | `frontend/components/dashboard/WorkspaceShell.tsx` |
| Brand | `frontend/lib/brand.ts` |

Setup: [vertex-ai-search-bigquery.md](../setup/vertex-ai-search-bigquery.md), [healthcare-api-fhir-export.md](../setup/healthcare-api-fhir-export.md), [document-ai-vertex-meddocs.md](../setup/document-ai-vertex-meddocs.md).

---

## 7. Remaining “100% production enterprise” items (explicit scope)

These are **not** required for a complete hackathon prototype but for a commercial product:

- SMART on FHIR EHR embed  
- Hosted Vertex AI Agent Engine / ADK runtime  
- AlloyDB / multi-tenant RBAC  
- Live meeting ingestion (STT, Calendar)  
- Formal HIPAA BAA and PHI environments  

JIVANA is **complete for the competition narrative** when all env vars are set and the demo script above passes.
