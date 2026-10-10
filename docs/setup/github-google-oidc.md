# GitHub Actions OIDC → Google Cloud (Workload Identity Federation)

**Status: MANUAL SETUP REQUIRED**

Deploy workflow (`.github/workflows/deploy.yml`) authenticates with **short-lived credentials** via GitHub OIDC and Google Workload Identity Federation (WIF). Do **not** store a service account JSON key in GitHub unless you have documented an unavoidable exception.

For this hackathon starter, use **one GCP project** for the deployed API.

## Prerequisites

- A GCP project with billing enabled (Cloud Run, Artifact Registry incur cost when used)
- `gcloud` CLI installed and authenticated as a human admin

Replace placeholders:

| Placeholder | Example | Where used |
|-------------|---------|------------|
| `GCP_PROJECT_ID` | `my-hackathon-123` | Deploy + GitHub variable |
| `REGION` | `asia-south1` | Artifact Registry + Cloud Run |
| `GITHUB_ORG` | `violinadoley` | WIF attribute condition |
| `GITHUB_REPO` | `project` | WIF attribute condition |

## 1. Enable APIs

```bash
gcloud config set project GCP_PROJECT_ID
gcloud services enable \
  iamcredentials.googleapis.com \
  sts.googleapis.com \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com
```

## 2. Create Artifact Registry repository

```bash
gcloud artifacts repositories create ai-hackathon \
  --repository-format=docker \
  --location=REGION \
  --description="API container images"
```

Set GitHub variable `GCP_ARTIFACT_REPO` to the repository name (e.g. `ai-hackathon`).

## 3. Create deploy service account

```bash
gcloud iam service-accounts create github-deploy \
  --display-name="GitHub Actions deploy"
```

Grant least privilege (adjust if you split frontend deploy):

```bash
SA="github-deploy@GCP_PROJECT_ID.iam.gserviceaccount.com"
gcloud projects add-iam-policy-binding GCP_PROJECT_ID \
  --member="serviceAccount:${SA}" \
  --role="roles/run.admin"
gcloud projects add-iam-policy-binding GCP_PROJECT_ID \
  --member="serviceAccount:${SA}" \
  --role="roles/artifactregistry.writer"
gcloud projects add-iam-policy-binding GCP_PROJECT_ID \
  --member="serviceAccount:${SA}" \
  --role="roles/iam.serviceAccountUser"
gcloud projects add-iam-policy-binding GCP_PROJECT_ID \
  --member="serviceAccount:${SA}" \
  --role="roles/secretmanager.secretAccessor"
```

**Firebase Hosting + rules** (same `github-deploy@…` service account): also grant `roles/firebasehosting.admin`, `roles/firebaserules.admin`, `roles/serviceusage.serviceUsageConsumer`, and `roles/firebasestorage.viewer`. Copy-paste commands in [firebase-backend.md](./firebase-backend.md#2-gcp-apis-and-cloud-run-service-account).

## 4. GitHub repo links (Website + Swagger variable)

**Settings → Actions → General → Workflow permissions** → **Read and write permissions** (required for `actions: write`).

- **Deploy API** tries to set `BACKEND_API_URL` after each deploy. If it logs HTTP 403, run locally (once per URL change):

  ```bash
  chmod +x scripts/set-github-repo-links.sh
  ./scripts/set-github-repo-links.sh \
    "https://YOUR_PROJECT_ID.web.app" \
    "https://YOUR_CLOUD_RUN_URL/docs"
  ```

- The GitHub **Website** field cannot always be updated from `GITHUB_TOKEN`; the script above sets homepage + variable with your `gh auth login` session.

## 5. Create Workload Identity Pool + Provider

```bash
gcloud iam workload-identity-pools create github-pool \
  --location=global \
  --display-name="GitHub Actions"

gcloud iam workload-identity-pools providers create-oidc github-provider \
  --location=global \
  --workload-identity-pool=github-pool \
  --display-name="GitHub" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --attribute-condition="assertion.repository=='GITHUB_ORG/GITHUB_REPO'" \
  --issuer-uri="https://token.actions.githubusercontent.com"
```

If create fails because the provider already exists, delete and retry:

```bash
gcloud iam workload-identity-pools providers delete github-provider \
  --location=global --workload-identity-pool=github-pool --quiet
```

Allow the GitHub identity to impersonate the deploy SA:

```bash
PROJECT_NUMBER=$(gcloud projects describe GCP_PROJECT_ID --format='value(projectNumber)')
gcloud iam service-accounts add-iam-policy-binding "${SA}" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/github-pool/attribute.repository/GITHUB_ORG/GITHUB_REPO"
```

## 6. GitHub repository Variables

**Settings → Secrets and variables → Actions → Variables**

| Variable | Value |
|----------|--------|
| `GCP_PROJECT_ID` | Your GCP project id |
| `GCP_REGION` | e.g. `asia-south1` |
| `GCP_ARTIFACT_REPO` | Artifact Registry repo name (e.g. `ai-hackathon`) |
| `GCP_WIF_PROVIDER` | Full provider resource name (see below) |
| `GCP_WIF_SERVICE_ACCOUNT` | `github-deploy@GCP_PROJECT_ID.iam.gserviceaccount.com` |

Provider resource name format:

```text
projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/providers/github-provider
```

Obtain with:

```bash
gcloud iam workload-identity-pools providers describe github-provider \
  --location=global \
  --workload-identity-pool=github-pool \
  --format='value(name)'
```

### Migrating from old `*_STAGING` variable names

If you already set `GCP_PROJECT_ID_STAGING`, etc., add the unsuffixed variables above with the same values, merge this rename, then delete the old `*_STAGING` variables.

## 7. GitHub Environment

**Settings → Environments → create `gcp`**

- Optional: **Deployment branches** → `develop` only
- Optional: required reviewers for first-time setup

The workflow references `environment: gcp` (not “staging” or “production”).

## 8. Secret Manager

```bash
echo -n "YOUR_GEMINI_API_KEY" | gcloud secrets create GEMINI_API_KEY --data-file=-
```

Cloud Run default compute service account needs `secretAccessor` on this secret:

```bash
PROJECT_NUMBER=$(gcloud projects describe GCP_PROJECT_ID --format='value(projectNumber)')
gcloud secrets add-iam-policy-binding GEMINI_API_KEY \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

## 9. Verify

1. Set all variables and create the `gcp` environment.
2. Push to `develop` (or run **Deploy API** manually) → workflow builds, deploys `ai-hackathon-api`, runs smoke tests.
3. Note the Cloud Run URL from the workflow log or Google Cloud Console.

## Cost note

WIF and IAM are free. Cloud Run, Artifact Registry storage, and Gemini API usage incur charges when services run.
