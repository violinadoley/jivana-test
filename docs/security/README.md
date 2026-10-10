# Security documentation

- [SECURITY.md](../../SECURITY.md) — reporting and policies
- [GitHub ↔ GCP OIDC](../setup/github-google-oidc.md) — deploy authentication
- PR template — security checklist on every change

## Pre-release checklist

- [ ] `AUTH_REQUIRED=true` in production
- [ ] Firestore rules deny unauthenticated writes where appropriate
- [ ] CORS limited to known frontend origins
- [ ] Secrets only in Secret Manager / GitHub environments
- [ ] Dependency audits reviewed
