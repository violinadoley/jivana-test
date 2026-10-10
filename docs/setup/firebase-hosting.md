# Firebase Hosting (free tier) — public frontend

**Cost:** Firebase **Spark (free)** plan includes Hosting for hackathon traffic. You still pay only if Gemini/Cloud Run usage exceeds free tiers elsewhere.

## Prerequisites

- Same GCP project as Cloud Run (`GCP_PROJECT_ID`)
- GitHub variables already used for API deploy (see [github-google-oidc.md](./github-google-oidc.md))
- **`PUBLIC_API_URL`** — Cloud Run base URL **without** trailing slash (e.g. `https://ai-hackathon-api-….run.app`)

## 1. Add Firebase to the GCP project

1. Open [Firebase Console](https://console.firebase.google.com/) → **Add project** → select your **existing** GCP project (`GCP_PROJECT_ID`).
2. Stay on the **Spark (free)** plan when prompted.
3. **Build → Hosting → Get started** (creates the default site `{projectId}.web.app`).  
   **Required** — deploy fails until this one-time step is done.

## 2. Enable API + IAM for GitHub deploy

```bash
export PROJECT_ID=YOUR_GCP_PROJECT_ID
export SA="github-deploy@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud config set project "$PROJECT_ID"
gcloud services enable firebasehosting.googleapis.com firebase.googleapis.com

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${SA}" \
  --role="roles/firebasehosting.admin"
```

Firestore/Storage **security rules** deploy in a second workflow job. Grant the same service account the rules roles in [firebase-backend.md](./firebase-backend.md#2-gcp-apis-and-cloud-run-service-account) so **Deploy Frontend** is fully green; otherwise Hosting still deploys but the workflow fails until rules IAM or the manual release checklist is satisfied.

## 3. GitHub repository variables

**Settings → Secrets and variables → Actions → Variables**

| Variable | Required | Example |
|----------|----------|---------|
| `PUBLIC_API_URL` | **Yes** | `https://ai-hackathon-api-….run.app` |
| `NEXT_PUBLIC_FIREBASE_API_KEY` | For Google login | Web app config — see [firebase-backend.md](./firebase-backend.md) |
| `NEXT_PUBLIC_FIREBASE_APP_ID` | For Google login | Web app config |
| `NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID` | For Google login | Web app config |
| `FIREBASE_STORAGE_BUCKET` | No | Defaults to `{GCP_PROJECT_ID}.firebasestorage.app` |
| `AUTH_REQUIRED` / `NEXT_PUBLIC_AUTH_REQUIRED` | No | `false` (default) |

Backend Firestore, Storage, and Auth: [firebase-backend.md](./firebase-backend.md).

Workflow: [`.github/workflows/deploy-frontend.yml`](../../.github/workflows/deploy-frontend.yml) on push to `develop`.

## 4. Verify

1. Merge to `develop` → **Deploy Frontend** (jobs **deploy-hosting** + **deploy-firebase-rules**) and **Deploy API** run.
2. In Actions, confirm **deploy-hosting** and **deploy-firebase-rules** succeeded; on failure, see [fallback rules steps](./firebase-backend.md#fallback-firebase-rules-if-ci-fails) or add IAM on `github-deploy@…`.
3. Open `https://YOUR_PROJECT_ID.web.app` → **Dashboard** → send a test message (hits Cloud Run via `NEXT_PUBLIC_API_URL`).
4. If the browser blocks requests, confirm **Deploy API** set `CORS_ORIGINS` to include `.web.app` and `.firebaseapp.com`.

## Local static preview

```bash
cd frontend
cp .env.local.example .env.local   # set NEXT_PUBLIC_API_URL to Cloud Run or localhost:8000
npm ci && npm run build && npm run preview
```
