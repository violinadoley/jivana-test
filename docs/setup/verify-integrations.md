# Verify JIVANA integrations

Use this checklist after deploying the API (Cloud Run or local) and configuring GCP console resources.

## Quick API checks

```bash
export API_BASE_URL=https://YOUR_CLOUD_RUN_URL   # no trailing slash
./scripts/smoke-api.sh
./scripts/verify-platform.sh
```

Optional live probes (institutional search + Vertex Search when configured):

```bash
./scripts/verify-platform.sh --probe
```

## Endpoint reference

| Endpoint | Purpose |
|----------|---------|
| `GET /health` | Liveness |
| `GET /ready` | Readiness |
| `GET /api/v1/platform/capabilities` | Per-integration configured flags |
| `GET /api/v1/platform/demo-readiness` | Core demo vs optional GCP checklist |
| `GET /api/v1/platform/demo-readiness?probe=true` | Same + lightweight live probes |

**Core demo** (no GCP console required): Gemini API key (or Vertex on Cloud Run), institutional knowledge corpus, discharge med rec APIs.

**Optional integrations** (console setup): Vertex AI Search, Document AI, Firestore activity, BigQuery productivity events, Healthcare FHIR export, Cloud Storage uploads.

## GCP console steps

Follow these guides in order when you want full platform green on `/platform/capabilities`:

1. [Vertex AI Search + BigQuery](./vertex-ai-search-bigquery.md)
2. [Document AI + med docs](./document-ai-vertex-meddocs.md)
3. [Healthcare API FHIR export](./healthcare-api-fhir-export.md)
4. [Firebase backend + Firestore](./firebase-backend.md)
5. GitHub Actions vars: [OIDC](./github-google-oidc.md) and deploy workflow env from the guides above

## ADK agents

Set `AGENT_BACKEND=auto` (default when `google-adk` is installed) or `adk` on Cloud Run. Use `legacy` to force template-only copilot, research, meetings, and workflow plan steps.

Med reconciliation stays deterministic (not ADK-driven).

## Hosted Agent Engine (optional)

In-process ADK on Cloud Run is the supported hackathon path. For a managed runtime upgrade, see [vertex-ai-agent-engine.md](./vertex-ai-agent-engine.md) (Phase 2).
