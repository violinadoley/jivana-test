# Starter template audit (2026-10-09)

Full audit performed against the AI Builder Cup starter (platform only). This document summarizes outcomes through **1.0.0**.

## Verdict

| Milestone | Status at 1.0.0 |
|-----------|---------------------|
| Local development | Ready |
| Onboarding (with GCP setup) | Ready |
| Hackathon cloud deploy (`develop`) | Ready |
| Strict multi-tenant production | Requires your auth/CORS/IAM choices |
| Competition feature work | Ready to start |

## Remediations (included in 1.0.0)

| ID | Topic | Fix |
|----|--------|-----|
| AUD-B-01 | Global activity leak | Per-user activity list; empty when anonymous |
| AUD-FB-02 | Prompts in Firestore | Metadata-only activity logs |
| AUD-FB-01 | Rules not in repo | Deny-all client Firestore/Storage rules + deploy |
| AUD-FB-03 | No auth tests | `backend/tests/test_auth.py` |
| AUD-G-01 / AUD-B-03 | Gemini blocking / timeout | `asyncio.to_thread` + 60s wait |
| AUD-FB-06 | Silent storage failure | Raise when storage configured |
| AUD-D-03 | `cloud` vs production | `is_production` includes `cloud` |
| AUD-B-04 | Test deps in image | pytest/httpx dev-only |
| Version drift | Pre-1.0 tags | Unified **1.0.0** first release |

## Still manual / external

- GitHub branch protection, WIF, Secret Manager, Firestore/Storage **console** first-time enable
- **`github-deploy@…` IAM** for rules deploy — documented in [firebase-backend.md](../setup/firebase-backend.md); [fallback](../setup/firebase-backend.md#fallback-firebase-rules-if-ci-fails) only if CI fails
- Optional: Sentry SDK, richer ai-evals datasets, Vitest
- Rotate PostHog project key if it was exposed in chat

## Verification (local)

Run before release:

```bash
cd backend && pip install -r requirements-dev.txt && ruff check app tests && mypy app && pytest -q
pytest ../ai-evals/regression -q
cd ../frontend && npm ci && npm run lint && npm run typecheck && npm run build
```

Docker build and Playwright require Docker Desktop and CI-equivalent environment respectively.
