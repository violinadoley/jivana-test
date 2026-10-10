# JIVANA — competition alignment (Future of Work · Healthcare)

**Full design & operations:** [jivana-design-and-operations.md](./jivana-design-and-operations.md)

## Problem statement (product target)

Transform how individuals and organizations in **healthcare** access knowledge, collaborate, make decisions, and complete everyday work—with measurable productivity, efficiency, knowledge accessibility, and workflow execution.

## Solution directions → product modules

| Direction | JIVANA module | API / stack |
|-----------|---------------|-------------|
| Enterprise knowledge assistant | Overview Q&A + **Copilot** tab | `/api/v1/copilot/chat`, Firestore sessions, institutional corpus |
| AI copilot | **Copilot** + **Workflow agent** | Vertex Gemini on Cloud Run |
| Document intelligence | **Documents** tab | Document AI, Vertex med rec, Healthcare FHIR export |
| Meeting intelligence | **Meetings** tab | `/api/v1/meetings/intelligence` |
| Workflow automation | **Workflows** tab + review queue | `/api/v1/workflows/agent-run`, human sign-off |
| Research assistant | **Research** tab | `/api/v1/research/synthesize` |
| Intelligent search | **Search** tab | Vertex AI Search + corpus (`/api/v1/search`) |

## Suggested Google Cloud technologies

| Technology | Status in app |
|------------|----------------|
| Gemini on Vertex AI | **Verified** (Cloud Run ADC) |
| Vertex AI Search | **Partial** — wire `VERTEX_SEARCH_DATA_STORE_ID` ([setup](../setup/vertex-ai-search-bigquery.md)) |
| Document AI | **Verified** in cloud when processor set |
| Workflow agent (knowledge → search → plan) | **Verified** — FastAPI orchestration with visible steps in UI |
| Vertex AI Agent Engine / Google ADK | **Optional / Phase 2** — hosted agent runtime; not required for end-to-end demo |
| Cloud Run | **Verified** |
| BigQuery | **Partial** — productivity event stream when dataset configured |
| Firestore | **Verified** — activity, copilot sessions, med rec jobs |
| Cloud Healthcare API | **Partial** — FHIR export after review |

## What judges should demo (15 min script)

Hybrid workspace on `/dashboard` (default): **Discharge med rec** tab first, then tool tabs.

1. **Discharge med rec** — demo trio → per-item review → finalize → HTML summary.  
2. **Search** — policy query (Vertex or corpus).  
3. **Meetings** — paste transcript → action items.  
4. **Copilot** — follow-up question with session memory.  
5. **Research** — cited synthesis.  
6. **Workflows** — agent plan with tool list.  
7. **Insights** — activity + BigQuery note.

## Still optional / Phase 2

- Native **Google ADK** / **Vertex AI Agent Engine** hosting (replace FastAPI tool loop).
- **AlloyDB** if relational reporting outgrows Firestore.
- Live **SMART on FHIR** EHR sidebar (export hook exists today).

No git push until local QA passes — see [backlog.md](./backlog.md).
