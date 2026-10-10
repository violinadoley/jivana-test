# Changelog

All notable changes to this project are documented here.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versioning follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

_Competition-specific product work._

### Changed

- Deploy workflows: `contents: write` for repo homepage; no `continue-on-error` on publish steps
- Docs: GitHub token permissions, PostHog key rotation, Firebase rules fallback (CI is primary)

## [1.0.0] - 2026-10-09

First release of the **AI hackathon starter** — Google-native platform (Next.js, FastAPI, Gemini, Firebase, Cloud Run) ready for competition-specific features.

### Platform

- Monorepo: Next.js static frontend, FastAPI on Cloud Run, Gemini `POST /api/v1/ai/generate`, file upload + GCS, activity feed
- CI: Ruff, mypy, pytest, Playwright e2e, ai-evals regression, Gitleaks, pip-audit, npm audit
- Deploy: GitHub Actions with WIF/OIDC — **Deploy API** (Cloud Run), **Deploy Frontend** (`deploy-hosting` + `deploy-firebase-rules`)
- Firebase Auth (Google), optional `AUTH_REQUIRED` / `DashboardAuthGate`, Admin SDK for Firestore and Storage from the API
- Deny-all client Firestore/Storage rules in repo; automated rules deploy when `github-deploy` IAM is configured
- Optional PostHog product analytics; security defaults and starter audit documented

### Security & privacy

- Per-user activity API; no prompt or model text in Firestore activity logs
- Token verification when Bearer tokens are sent; auth tests in `backend/tests/test_auth.py`

### Documentation

- Setup: OIDC, Firebase Hosting/backend, branch protection, PostHog
- [Starter template complete](docs/starter-template.md) — customize prompts and UI from here

[Unreleased]: https://github.com/violinadoley/project/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/violinadoley/project/releases/tag/v1.0.0
