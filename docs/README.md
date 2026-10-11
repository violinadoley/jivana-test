# JIVANA documentation

Start here if you are new to the repository.

## Essential

| Document | Purpose |
|----------|---------|
| [../README.md](../README.md) | Repo overview, stack, CI/CD |
| [development/team-onboarding.md](development/team-onboarding.md) | Local setup (Tier A/B/C env) |
| [development/environment-variables.md](development/environment-variables.md) | All env vars |
| [product/jivana-design-and-operations.md](product/jivana-design-and-operations.md) | Product architecture and flows |
| [product/backlog.md](product/backlog.md) | Shipped vs optional work |

## Development

| Document | Purpose |
|----------|---------|
| [development/workflow.md](development/workflow.md) | Branching, PRs, deploy cadence |
| [development/testing-strategy.md](development/testing-strategy.md) | pytest, Playwright, ai-evals |
| [development/team-invite-message.md](development/team-invite-message.md) | Copy-paste invite for teammates |
| [../CONTRIBUTING.md](../CONTRIBUTING.md) | Git author policy (no bot co-authors) |

## Setup and cloud

| Document | Purpose |
|----------|---------|
| [setup/github-google-oidc.md](setup/github-google-oidc.md) | GitHub Variables, WIF, first deploy |
| [setup/firebase-hosting.md](setup/firebase-hosting.md) | Frontend Hosting |
| [setup/firebase-backend.md](setup/firebase-backend.md) | Auth, Firestore, Storage rules |
| [setup/verify-integrations.md](setup/verify-integrations.md) | Post-deploy smoke |
| [setup/document-ai-vertex-meddocs.md](setup/document-ai-vertex-meddocs.md) | Med rec intake |
| [setup/vertex-ai-search-bigquery.md](setup/vertex-ai-search-bigquery.md) | Search + analytics |
| [setup/healthcare-api-fhir-export.md](setup/healthcare-api-fhir-export.md) | FHIR export |
| [setup/smart-on-fhir.md](setup/smart-on-fhir.md) | SMART launch + OAuth client |
| [setup/vertex-ai-agent-engine.md](setup/vertex-ai-agent-engine.md) | Optional Agent Engine |

## Architecture

| Document | Purpose |
|----------|---------|
| [architecture.md](architecture.md) | System diagram and security model |
| [architecture/technology-capability-matrix.md](architecture/technology-capability-matrix.md) | Verified vs planned integrations |
| [architecture/technology-decision-process.md](architecture/technology-decision-process.md) | How to propose new tech |
| [architecture/healthcare-google-cloud.md](architecture/healthcare-google-cloud.md) | Healthcare API context |

## Operations

| Document | Purpose |
|----------|---------|
| [deployment.md](deployment.md) | Deploy overview |
| [deployment/cloud-run.md](deployment/cloud-run.md) | API service details |
| [runbooks/rollback.md](runbooks/rollback.md) | Roll back Cloud Run / Hosting |
| [security-defaults.md](security-defaults.md) | Auth and public API defaults |
| [observability.md](observability.md) | Logging and debugging |

## AI quality

| Document | Purpose |
|----------|---------|
| [../ai-evals/README.md](../ai-evals/README.md) | Prompt regression framework |

## Historical

| Document | Purpose |
|----------|---------|
| [starter-template.md](starter-template.md) | Platform baseline (v1.0.0) |
| [audits/starter-template-audit.md](audits/starter-template-audit.md) | Platform audit snapshot (2026-10-09) |
