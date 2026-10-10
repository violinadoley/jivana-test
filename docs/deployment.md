# Deployment

Replace placeholder project IDs and regions with your own values. Do not commit secrets.

**Automated deploy (after GCP setup):**

- [Cloud Run API (`develop`)](deployment/cloud-run.md) — `.github/workflows/deploy.yml`
- [GitHub OIDC → GCP](setup/github-google-oidc.md) — **MANUAL SETUP REQUIRED**

## 1. Google Cloud project

1. Create or select a project in [Google Cloud Console](https://console.cloud.google.com/).
2. Enable billing (required for Cloud Run and some APIs).

Enable APIs:

```bash
gcloud services enable run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  firestore.googleapis.com \
  storage.googleapis.com
```

## 2. Gemini

1. Create an API key in [Google AI Studio](https://aistudio.google.com/apikey).
2. Store it in Secret Manager:

```bash
echo -n "YOUR_GEMINI_API_KEY" | gcloud secrets create GEMINI_API_KEY --data-file=-
```

## 3. Firebase

1. Add Firebase to the same GCP project in [Firebase Console](https://console.firebase.google.com/).
2. Enable **Authentication** (e.g. Google provider) and **Firestore** / **Storage** as needed.
3. Register a web app and copy client config into frontend env vars (`NEXT_PUBLIC_FIREBASE_*`).
4. For backend Admin SDK on Cloud Run, use the default service account or attach a service account with Firestore/Storage roles.

Update `frontend/.firebaserc` with your Firebase project ID.

## 4. Deploy backend to Cloud Run

From the repository root:

```bash
gcloud run deploy ai-hackathon-api \
  --source ./backend \
  --region YOUR_REGION \
  --allow-unauthenticated \
  --set-env-vars "GEMINI_MODEL=gemini-2.5-flash,AUTH_REQUIRED=false,FIREBASE_PROJECT_ID=YOUR_PROJECT_ID,FIREBASE_STORAGE_BUCKET=YOUR_BUCKET.appspot.com,ENVIRONMENT=production,CORS_ORIGINS=https://YOUR_FRONTEND_DOMAIN" \
  --set-secrets "GEMINI_API_KEY=GEMINI_API_KEY:latest"
```

Alternatively build and push a container:

```bash
gcloud builds submit --tag REGION-docker.pkg.dev/PROJECT_ID/REPO/ai-hackathon-api ./backend
gcloud run deploy ai-hackathon-api --image REGION-docker.pkg.dev/PROJECT_ID/REPO/ai-hackathon-api --region YOUR_REGION
```

Note the **Cloud Run service URL** (e.g. `https://ai-hackathon-api-xxxxx-REGION.a.run.app`).

## 5. Configure frontend

Set in your hosting environment (or `.env.production.local` for build):

```env
NEXT_PUBLIC_API_URL=https://YOUR_CLOUD_RUN_URL
```

## 6. Deploy frontend

**Option A — Firebase App Hosting (recommended for full Next.js SSR)**

Follow [Firebase App Hosting](https://firebase.google.com/docs/app-hosting) to connect this repo’s `frontend` directory to GitHub and deploy with environment variables configured in the console.

**Option B — Static export + Firebase Hosting**

If you configure `output: 'export'` in `next.config.ts` and run `next build`, deploy the `out` directory:

```bash
cd frontend
npm run build
firebase deploy --only hosting
```

Adjust `firebase.json` rewrites for your routing strategy.

## 7. Verify

1. `curl https://YOUR_CLOUD_RUN_URL/health`
2. Open the hosted frontend, use the dashboard to send a message and upload a test `.txt` file.
3. When enabling auth, set `AUTH_REQUIRED=true` on Cloud Run and configure Firebase on both sides.

## GitHub → Google Cloud (later)

- Connect Cloud Build or Cloud Run continuous deployment to your GitHub repository.
- Keep CI in `.github/workflows/ci.yml` for tests on every PR; add a separate deploy workflow when you are ready for production automation.
