# ADR-006: GitHub Actions for CI/CD

## Context

Team uses GitHub; want native PR checks and deploys without extra SaaS.

## Decision

**GitHub Actions** for CI and Cloud Run deploy (`develop` → **Deploy API**) with **OIDC → GCP WIF**.

## Alternatives considered

- Cloud Build triggers only — weaker PR integration
- Jenkins / CircleCI — unnecessary complexity

## Consequences

- Manual one-time WIF setup documented in `docs/setup/github-google-oidc.md`
- No long-lived GCP keys in GitHub
