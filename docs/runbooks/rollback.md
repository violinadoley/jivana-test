# Rollback runbook

**MANUAL SETUP REQUIRED:** You must have previously deployed at least one known-good revision.

## Identify current and previous deployment

1. GitHub → **Actions** → **Deploy API** → note commit SHA of last green deploy.
2. Cloud Console → **Cloud Run** → `ai-hackathon-api` → **Revisions**.

Each revision should correspond to an image tag (`git SHA`).

## Roll back Cloud Run (API)

```bash
gcloud config set project GCP_PROJECT_ID
gcloud run services describe ai-hackathon-api \
  --region REGION \
  --format='yaml(status.traffic,status.latestReadyRevisionName)'

# Route 100% traffic to a previous revision
gcloud run services update-traffic ai-hackathon-api \
  --region REGION \
  --to-revisions REVISION_NAME=100
```

Or redeploy a known-good image:

```bash
gcloud run deploy ai-hackathon-api \
  --region REGION \
  --image REGION-docker.pkg.dev/PROJECT/REPO/ai-hackathon-api:GOOD_SHA
```

## Roll back frontend

- **Firebase Hosting / App Hosting:** redeploy previous build from git tag or Hosting release history in Firebase Console.
- Document your team’s frontend host; this starter focuses on API automation first.

## Database / schema

Firestore schema changes are **not** automatically rolled back with Cloud Run. If a bad deploy wrote incompatible documents:

1. Stop traffic to bad revision.
2. Deploy fixed application code forward-fixing reads.
3. Run a one-off migration script against the hackathon GCP project first.

See [database.md](database.md).

## Verify recovery

```bash
API_BASE_URL=https://YOUR_SERVICE_URL scripts/smoke-api.sh
```

Run critical Playwright flows against production UI if applicable.

## Approval

Production rollback should be approved by a team lead. Record incident in GitHub Issue.
