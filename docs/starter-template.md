# Platform baseline (v1.0.0)

The repository began as an **AI hackathon starter**; **JIVANA** is the product built on that platform. Infrastructure below remains the foundation for all features.

## Platform capabilities

| Capability | Where |
|------------|--------|
| CI (lint, test, security, e2e) | `.github/workflows/ci.yml` |
| API deploy (Cloud Run + WIF) | `.github/workflows/deploy.yml` |
| UI deploy (Firebase Hosting + rules) | `.github/workflows/deploy-frontend.yml` |
| Gemini + ADK on API | `backend/app/ai/` |
| File upload + GCS | `POST /api/v1/files/upload` |
| Activity feed | `GET /api/v1/activity` |
| Google sign-in | Firebase Auth + optional `AUTH_REQUIRED` |
| Security | [security-defaults.md](security-defaults.md), Gitleaks, pip-audit |

## JIVANA product (on `develop`)

Discharge med rec workbench, enterprise workspace tabs, Vertex Search, Document AI, FHIR export, SMART launch, BigQuery events — see [product/jivana-design-and-operations.md](product/jivana-design-and-operations.md) and [product/backlog.md](product/backlog.md).

## First-time GCP / GitHub setup

1. [setup/github-google-oidc.md](setup/github-google-oidc.md)
2. [setup/firebase-hosting.md](setup/firebase-hosting.md)
3. [setup/firebase-backend.md](setup/firebase-backend.md)

## New team members

[development/team-onboarding.md](development/team-onboarding.md) · [development/environment-variables.md](development/environment-variables.md)

## Architecture reference

- [architecture/technology-capability-matrix.md](architecture/technology-capability-matrix.md)
- [architecture/technology-decision-process.md](architecture/technology-decision-process.md)

## Version

Platform tagged **v1.0.0** — see [CHANGELOG](../CHANGELOG.md).
