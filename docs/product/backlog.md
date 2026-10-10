# JIVANA product backlog

**Canonical design:** [jivana-design-and-operations.md](./jivana-design-and-operations.md)

## Shipped (local — verify before push)

- [x] Eight workspace modules (overview, copilot, search, documents, meetings, research, workflows, insights)
- [x] Platform capabilities API + UI
- [x] Multi-step workflow agent with visible tool steps
- [x] Research UI shows sources
- [x] Deploy workflow env for Vertex Search, BigQuery, Healthcare FHIR
- [x] Institutional knowledge + Vertex Search merge

## GCP console (your project)

- [ ] Create Vertex AI Search data store + ingest policy corpus
- [ ] Create BigQuery `productivity_events` table + IAM
- [ ] Create Healthcare FHIR store + IAM (if demoing FHIR export)
- [ ] Set GitHub Actions vars matching [vertex-ai-search-bigquery.md](../setup/vertex-ai-search-bigquery.md)

## Phase 2 (post-hackathon)

- [x] Google ADK in-process agents (copilot, research, meetings, workflow plan) — `AGENT_BACKEND`
- [x] `GET /platform/demo-readiness` + `scripts/verify-platform.sh`
- [ ] Vertex AI Agent Engine hosted runtime (optional — see `docs/setup/vertex-ai-agent-engine.md`)
- [ ] SMART on FHIR EHR embed
- [x] Playwright hybrid workspace tab journey (CI)
- [ ] Playwright against deployed URL with live API
- [ ] OG images / favicon final brand
- [ ] Archive legacy `violinadoley/project` repo
