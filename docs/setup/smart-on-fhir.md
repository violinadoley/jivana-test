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

Set GitHub / Cloud Run vars when you register a SMART app with your EHR vendor or Google Healthcare API test harness.

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
