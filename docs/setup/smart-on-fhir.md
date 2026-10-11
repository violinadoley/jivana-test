# SMART on FHIR EHR embed

JIVANA exposes SMART **configuration** and a **launch landing page** so you can wire an EHR sandbox. Full OAuth against a live EHR is project-specific.

## Verified in repo

| Piece | Location |
|-------|----------|
| SMART config JSON | `GET /api/v1/smart/configuration` |
| Launch redirect | `GET /api/v1/smart/launch?iss=...&launch=...` → Hosting `/smart/launch` |
| Workspace UI | `frontend/app/smart/launch/page.tsx` |

## Environment (optional)

```env
SMART_CLIENT_ID=
SMART_FHIR_ISS=https://healthcare.googleapis.com/v1/projects/PROJECT/locations/LOC/datasets/DS/fhirStores/STORE/fhir
SMART_APP_LAUNCH_URL=https://YOUR_PROJECT.web.app/smart/launch
```

Set **GitHub Actions → Variables** (same list as `GCP_PROJECT_ID`; deployed to Cloud Run by [deploy.yml](../../.github/workflows/deploy.yml)):

| Variable | Example (JIVANA prod) |
|----------|------------------------|
| `SMART_APP_LAUNCH_URL` | `https://project-bf77a013-c0b3-413c-a75.web.app/smart/launch` |
| `SMART_FHIR_ISS` | `https://healthcare.googleapis.com/v1/projects/PROJECT/locations/asia-south1/datasets/jivana-health/fhirStores/jivana-fhir/fhir` |
| `SMART_CLIENT_ID` | OAuth 2.0 **Web client** id (see below) |
| `NEXT_PUBLIC_SITE_URL` | `https://project-bf77a013-c0b3-413c-a75.web.app` (frontend build / Open Graph) |

`GET /api/v1/platform/capabilities` marks **SMART on FHIR** as configured when both `SMART_CLIENT_ID` and `SMART_APP_LAUNCH_URL` are set on Cloud Run.

### Register `SMART_CLIENT_ID` (Google Cloud Console — one time)

1. Open [Credentials](https://console.cloud.google.com/apis/credentials?project=project-bf77a013-c0b3-413c-a75) for your GCP project.
2. If prompted, configure the **OAuth consent screen** (External + test users is fine for hackathon).
3. **Create credentials → OAuth client ID → Web application**.
4. **Authorized redirect URIs** (add both):
   - `https://project-bf77a013-c0b3-413c-a75.web.app/smart/launch`
   - `https://project-bf77a013-c0b3-413c-a75.firebaseapp.com/smart/launch`
5. Copy the **Client ID** (not the secret for public SMART apps).
6. Set GitHub variable: `gh variable set SMART_CLIENT_ID --body "YOUR_CLIENT_ID.apps.googleusercontent.com" --repo OWNER/REPO`
7. Re-run **Deploy API** (push to `develop` or workflow dispatch) so Cloud Run picks up the id.

Token exchange and FHIR authorization are **not** implemented in the demo API; the client id proves app registration for judges and enables a future OAuth implementation.

## Demo flow

1. Open `https://YOUR_PROJECT.web.app/smart/launch` (or follow API redirect from `/api/v1/smart/launch`).
2. Confirm launch context display (ISS / launch token when present).
3. **Open workspace** → discharge med rec with session context banner.

## Production checklist

- [ ] Register SMART app (client id, redirect URIs) with EHR or FHIR store
- [ ] Implement authorization code exchange (token endpoint) — **not** in demo stub
- [ ] Map `fhirUser` / patient context to Firebase Auth or session cookie
- [ ] HIPAA assessment before real PHI

See also [healthcare-api-fhir-export.md](./healthcare-api-fhir-export.md).
