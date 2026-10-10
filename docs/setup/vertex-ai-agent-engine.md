# Vertex AI Agent Engine (optional Phase 2)

JIVANA runs **Google ADK in-process** on Cloud Run today (`AGENT_BACKEND=auto|adk`). That covers copilot, research, meetings, and workflow planning with shared knowledge/search tools.

**Vertex AI Agent Engine** is an optional upgrade when you need:

- Managed scaling and session isolation separate from the API container
- Long-running agent sessions without tying them to HTTP request lifetimes
- Google-hosted agent runtime policies and observability

## Current state

| Layer | Status |
|-------|--------|
| ADK agents in `backend/app/ai/adk/` | Implemented |
| Cloud Run + `AGENT_BACKEND` | Supported |
| Agent Engine deployment manifest | Not in repo — manual GCP setup |

## Migration outline (when approved)

1. Extract agent definitions from `agents_*.py` into an ADK app bundle suitable for Agent Engine.
2. Deploy the bundle to Agent Engine in your GCP project (region aligned with Vertex AI).
3. Point FastAPI routes to Agent Engine **session/run APIs** instead of `run_agent_text` in-process.
4. Keep med rec, Document AI intake, and FHIR export on the existing API service.
5. Update IAM: Cloud Run service account needs Agent Engine invoke permissions; no long-lived keys in GitHub.

## Placeholders (fill when you create resources)

| Setting | Example placeholder |
|---------|---------------------|
| `GCP_PROJECT_ID` | `your-hackathon-project` |
| `VERTEX_AGENT_ENGINE_ID` | `(from console after deploy)` |
| `VERTEX_LOCATION` | `us-central1` |

Do not commit service account JSON. Use Workload Identity Federation for CI per [github-google-oidc.md](./github-google-oidc.md).

## Related docs

- [verify-integrations.md](./verify-integrations.md)
- [technology-capability-matrix.md](../architecture/technology-capability-matrix.md)
