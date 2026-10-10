# Development workflow

## Environments

| Environment | Where it runs | Data |
|-------------|---------------|------|
| Local | localhost | Dev Firebase / emulators / dev Gemini key |
| Cloud | Cloud Run (`ai-hackathon-api`) | Your hackathon GCP project |

## Daily flow

1. Pick or create GitHub Issue
2. `git checkout develop && git pull`
3. `git checkout -b feature/...`
4. Implement + tests
5. Open PR → `develop` → CI green → review → merge
6. **Deploy API** runs on push to `develop` (when GCP variables are set)
7. Smoke-test the Cloud Run URL; point the frontend at it when ready

## `main` branch

`main` stays the stable line for releases and branch protection. This starter does **not** deploy a second environment from `main` — only `develop` triggers Cloud Run deploy. Merge `develop` → `main` when you want `main` to match what you demoed.

## Emergency

Document any direct push to `main` in CHANGELOG and open a follow-up PR to sync `develop`.
