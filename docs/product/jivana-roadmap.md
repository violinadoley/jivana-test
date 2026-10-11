# JIVANA — demo and competition alignment

**Design and operations:** [jivana-design-and-operations.md](./jivana-design-and-operations.md)  
**Backlog:** [backlog.md](./backlog.md)

## Problem statement

Healthcare teams lose time when knowledge is scattered and when medication lists disagree at care transitions without auditable human review.

## Product modules

| Module | UI | API |
|--------|-----|-----|
| Discharge / admission / transfer med rec | **Discharge med rec** tab | `/api/v1/meddocs/cases`, reconcile, review, finalize |
| Copilot | **Copilot** tab | `/api/v1/copilot/chat` |
| Search | **Search** tab | `/api/v1/search` |
| Meetings | **Meetings** tab | `/api/v1/meetings/intelligence` |
| Research | **Research** tab | `/api/v1/research/synthesize` |
| Workflows | **Workflows** tab | `/api/v1/workflows/agent-run` |
| Insights | **Insights** tab | `/api/v1/analytics/productivity` |
| SMART embed | `/smart/launch` | `/api/v1/smart/*` |

## Google Cloud integration status (production project)

| Technology | Status |
|------------|--------|
| Gemini on Vertex AI (Cloud Run ADC) | **Verified** |
| Google ADK (in-process) | **Verified** |
| Vertex AI Search | **Verified** when data store configured |
| Document AI | **Verified** when processor configured |
| Firestore / Storage | **Verified** |
| BigQuery productivity events | **Verified** when dataset configured |
| Cloud Healthcare FHIR export | **Verified** when store configured |
| SMART on FHIR (launch + config) | **Verified**; OAuth token exchange not implemented |
| Vertex AI Agent Engine | **Optional** — stub env only; ADK on Cloud Run is production path |

Setup pointers: [docs/README.md](../README.md).

## Suggested demo script (~15 min)

On `/dashboard` (MVP workbench):

1. **Discharge med rec** — create case → reconcile → per-item review → finalize → summary  
2. **Search** — policy query  
3. **Meetings** — transcript → actions  
4. **Copilot** — follow-up with session  
5. **Research** — cited synthesis  
6. **Workflows** — agent plan with tool steps  
7. **Insights** — activity and med-rec metrics  

Optional: `/smart/launch` → workspace.

## Phase 2 (optional)

- Vertex AI **Agent Engine** hosting for ADK (see [vertex-ai-agent-engine.md](../setup/vertex-ai-agent-engine.md))
- Full **SMART OAuth** and patient context sessions
- **AlloyDB** if reporting outgrows Firestore
