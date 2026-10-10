---
name: architecture-proposal
description: >-
  Evaluate a user-provided idea or feature and propose architecture using the
  starter matrix and MCP catalogue. Use when the user asks for architecture,
  technology choice, workflow design, or feature planning—not for choosing
  the product idea.
disable-model-invocation: true
---

# Architecture proposal

## Preconditions

- The **product idea comes from the user**. If none was given, ask for problem, users, data, and constraints—do not invent a competition concept.
- Do not install MCPs, add dependencies, change cloud resources, or deploy.

## Workflow

1. Read `docs/architecture/technology-capability-matrix.md`.
2. Read `docs/architecture/mcp-and-tooling-catalogue.md` when integrations or MCPs may apply.
3. Read `docs/architecture/technology-decision-process.md`.
4. Inspect the repo (`backend/app/`, `frontend/`, `.github/workflows/`, env examples).
5. Clarify user, problem, data sources, workflow, and non-goals.
6. Mark what must be **deterministic** (auth, validation, quotas) vs **model-backed**.
7. Map relevant **AI Builder Cup category technologies** only as optional references—never as a product recommendation.
8. Compare options; recommend the **simplest viable** architecture on the current starter.
9. List MCPs/tools needed for **implementation support** (not production runtime) with permissions and read vs write.
10. List technologies and MCPs **not** to introduce and why.
11. Assess cost, quotas, privacy, security, latency, ops complexity, and evaluation (`ai-evals/`).
12. Deliver:
    - Mermaid architecture diagram
    - Data flow (bullets)
    - API outline (routes/events)
    - Implementation milestones (ordered)
13. **Stop and wait for explicit user approval** before application code, dependencies, MCP install, IAM, or deploy.

## Output template

Use headings:

**Context** | **Goals** | **Non-goals** | **Recommended architecture** | **Alternatives considered** | **Data flow** | **API sketch** | **Milestones** | **MCP/dev tools** | **Risks** | **Evaluation** | **Approval required**
