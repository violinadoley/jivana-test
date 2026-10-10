# Cost management

This project targets **free or low-cost** Google Cloud and GitHub tooling.

## Likely costs

| Service | Cost driver | Mitigation |
|---------|-------------|------------|
| Cloud Run | Requests, CPU time, min instances | `min-instances=0`, low `max-instances`, short timeouts |
| Artifact Registry | Stored image GB | Lifecycle policy / delete old tags |
| Gemini API | Tokens per request | Cache, batch, eval on subset, avoid live eval on every PR |
| Firestore | Reads/writes/storage | Index only what you query; emulator locally |
| Firebase Hosting | Bandwidth | Static assets, CDN defaults |
| GitHub Actions | Minutes | Concurrency cancel on CI, path filters later if needed |

## CI

- AI live calls in CI should stay **mocked** until you add a scheduled cloud eval job.
- Playwright runs only Chromium in CI.

## Production

- Require auth in production (`AUTH_REQUIRED=true`) to reduce abuse-driven API cost.
- Set Cloud Run max instances cap (workflow default: 5).

## Monitoring spend

1. GCP **Billing → Budgets** — alert at 50% / 90% of team budget.
2. Review **Gemini** usage in Google AI Studio / Cloud billing reports.

## What is free

- GitHub public repos: Actions minutes (within quota)
- Workload Identity Federation
- Cloud Logging (within free tier limits)
