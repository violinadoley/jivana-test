# JIVANA product backlog

**Canonical design:** [jivana-design-and-operations.md](./jivana-design-and-operations.md)

## Shipped (production — project-bf77a013-c0b3-413c-a75)

- [x] Hybrid workspace + discharge-first med rec workbench
- [x] Platform capabilities + demo-readiness + verify scripts
- [x] GCP: Vertex Search, BigQuery, Document AI, FHIR, Firestore, ADK on Cloud Run
- [x] Admission / transfer / discharge case types (API + UI)
- [x] SMART on FHIR config + launch page (demo stub; OAuth in prod is manual)
- [x] Agent Engine env hook + in-process ADK fallback
- [x] Playwright local tab journey + deployed hosting smoke (`npm run test:e2e:deployed`)
- [x] Open Graph / Twitter metadata + favicon
- [x] Legacy `violinadoley/project` repo archived

## Optional hardening (when you have EHR vendor access)

- [ ] Full SMART OAuth token exchange + patient context session
- [ ] Deploy agents to Vertex AI Agent Engine and set `VERTEX_AGENT_ENGINE_ID`
- [ ] Set `SMART_CLIENT_ID` + `SMART_APP_LAUNCH_URL` on Cloud Run / GitHub vars

## Competition / polish

- [ ] 3-minute demo video + submission URL
- [ ] Custom OG image asset (currently uses hero photo)
