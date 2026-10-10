# Technology decision process

This repository is a **platform starter** for AI Builder Cup 2026. The **product idea is chosen by the team**—agents and contributors must not propose, generate, rank, or steer toward a particular competition concept.

## When to use this process

- A feature might add a GCP service, npm/pip package, database, vector store, or MCP
- You need to align with **category-suggested** Google technologies (reference only)
- Architecture review before non-trivial implementation

## Steps

1. **Capture inputs** from the team: users, problem, data sources, workflow, constraints, and demo goals—not invented by the agent.
2. **Read** [technology-capability-matrix.md](./technology-capability-matrix.md) and note what is **Verified** vs **Planned** vs **Absent** in this repo.
3. **Read** [mcp-and-tooling-catalogue.md](./mcp-and-tooling-catalogue.md) if IDE or cloud developer integration is involved.
4. **Inspect the repository**—`backend/app/`, `frontend/`, `.github/workflows/`, env examples; extend existing patterns in `backend/app/ai/` and API routes.
5. **Separate AI from deterministic logic**—auth, validation, quotas, PII handling, and billing belong in code; use models for language, reasoning, classification, or extraction where justified.
6. **Compare options**—prefer the simplest path on the current stack (Gemini API + FastAPI + Firestore/GCS + Cloud Run/Hosting).
7. **Record hard choices**—add a short ADR under `docs/adr/` when a decision is costly or hard to reverse.
8. **Approval gate**—use [.cursor/skills/architecture-proposal/SKILL.md](../../.cursor/skills/architecture-proposal/SKILL.md) for structured proposals; do not add dependencies, MCPs, IAM changes, or deploys until the team approves.

## AI Builder Cup 2026 — category technology reference

Suggested technologies from challenge descriptions (**not mandatory**; see matrix for starter status):

| Category | Suggested technologies |
|----------|------------------------|
| **BFSI** | Gemini on Vertex AI, BigQuery, predictive ML, Document AI, Vertex AI Search / Agent Search, Cloud Run, Cloud SQL, AlloyDB, Pub/Sub |
| **Retail & Commerce** | Gemini on Vertex AI, Vertex AI Search / Agent Search, BigQuery, BigQuery AI, Cloud Run, Cloud Storage, AlloyDB, Cloud SQL, Looker |
| **Manufacturing** | Gemini on Vertex AI, predictive ML, BigQuery, Cloud Storage, Vision AI, Pub/Sub, Dataflow, Cloud Run |
| **Media, Content & Digital Experiences** | Gemini on Vertex AI, Imagen, Veo, Speech-to-Text, Text-to-Speech, Cloud Translation, BigQuery, Cloud Storage, Cloud Run |
| **Future of Work & Enterprise Productivity** | Gemini on Vertex AI, Vertex AI Search / Agent Search, Document AI, Vertex AI Agent Engine, Google ADK, Cloud Run, BigQuery, AlloyDB, Firestore |
| **Sustainability & Social Impact** | Gemini on Vertex AI, BigQuery, predictive ML, Earth Engine, Cloud Storage, Vision AI, Cloud Run, Pub/Sub |

## Maintaining the baseline

When an **approved** change adds a service, dependency, or MCP, update the matrix and catalogue in the same PR (or an immediate follow-up).

## Healthcare track (team direction)

Clinical and imaging data standards: [healthcare-google-cloud.md](./healthcare-google-cloud.md) → [Cloud Healthcare API documentation](https://docs.cloud.google.com/healthcare-api/docs). Product scope still defined by the team; use an architecture proposal before enabling the API or storing PHI.

## Related documentation

- [docs/architecture.md](../architecture.md) — system diagram and extension points
- [docs/starter-template.md](../starter-template.md) — platform completeness checklist
- [docs/mcp.md](../mcp.md) — MCP servers configured for this repo
- [CONTRIBUTING.md](../../CONTRIBUTING.md) — branching and quality gates
- [.cursor/rules/architecture-standards.mdc](../../.cursor/rules/architecture-standards.mdc)
