# Starter template (platform complete)

This document marks the **infrastructure starter** as complete. Competition-specific product work starts after this point.

## What is included

| Capability | Where |
|------------|--------|
| CI (lint, test, security, e2e) | `.github/workflows/ci.yml` |
| API deploy (Cloud Run + WIF) | `.github/workflows/deploy.yml` |
| UI deploy (Firebase Hosting + rules) | `.github/workflows/deploy-frontend.yml` (`deploy-hosting`, `deploy-firebase-rules`) |
| Gemini HTTP API | `POST /api/v1/ai/generate` |
| File upload + GCS | `POST /api/v1/files/upload` |
| Activity feed | `GET /api/v1/activity`, dashboard **Recent activity** |
| Google sign-in | Firebase Auth + optional `AUTH_REQUIRED` |
| Security policy | [security-defaults.md](security-defaults.md), Gitleaks + pip-audit in CI |
| Product analytics (optional) | [setup/posthog.md](setup/posthog.md) — funnels & demo evidence, not AI quality |

## First-time GCP / GitHub setup

1. [github-google-oidc.md](setup/github-google-oidc.md)
2. [firebase-hosting.md](setup/firebase-hosting.md)
3. [firebase-backend.md](setup/firebase-backend.md)

## Architecture and tooling reference

- [architecture/technology-decision-process.md](architecture/technology-decision-process.md)
- [architecture/technology-capability-matrix.md](architecture/technology-capability-matrix.md)
- [architecture/mcp-and-tooling-catalogue.md](architecture/mcp-and-tooling-catalogue.md)
- [architecture/healthcare-google-cloud.md](architecture/healthcare-google-cloud.md) — [Cloud Healthcare API](https://docs.cloud.google.com/healthcare-api/docs) (healthcare track)

## Day-to-day workflow

1. Branch from `develop` → PR → merge to `develop` (deploys API + frontend).
2. Periodically merge `develop` → `main` for a stable snapshot (no extra deploy on `main` alone).
3. Customize prompts under `backend/app/ai/`, routes under `backend/app/api/`, UI under `frontend/`.

## Version

Starter baseline: **v1.0.0** (see [CHANGELOG](../CHANGELOG.md)).
