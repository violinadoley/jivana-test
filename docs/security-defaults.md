# Security defaults (starter template)

Deliberate choices for the hackathon starter. Change them when you harden for a public competition demo or production.

## Authentication

| Setting | Default | Where |
|---------|---------|--------|
| `AUTH_REQUIRED` | `false` | Cloud Run deploy ([deploy.yml](../.github/workflows/deploy.yml)) |
| `NEXT_PUBLIC_AUTH_REQUIRED` | `false` | Frontend build ([deploy-frontend.yml](../.github/workflows/deploy-frontend.yml)) |

**Behavior today**

- API routes accept requests **without** a Bearer token.
- If the user signs in on the web app, the frontend sends a Firebase ID token; the API **verifies** it when present and attaches `user_id` to activity logs.
- **Activity feed:** `GET /api/v1/activity` returns items **only for the signed-in user**. Without a valid Bearer token it returns an empty list (even when `AUTH_REQUIRED=false`). Activity documents store **metadata only** (no prompts or model text).
- To require login everywhere: set **`AUTH_REQUIRED=true`** and **`NEXT_PUBLIC_AUTH_REQUIRED=true`** in GitHub Actions variables, then redeploy API + frontend.

Firebase **Google** sign-in must stay enabled in the console. Firestore is accessed only via the **Admin SDK** on Cloud Run (not direct client reads).

## Public API surface

Cloud Run is deployed with **`--allow-unauthenticated`**. That is intentional for judges and quick demos. Tighten with Cloud Run IAM + `AUTH_REQUIRED` when you need it.

## GitHub Actions variables (naming)

| Variable | Meaning |
|----------|---------|
| **`PUBLIC_API_URL`** | Cloud Run **base URL** (no trailing slash). Used as `NEXT_PUBLIC_API_URL` in the frontend build. Example: `https://ai-hackathon-api-….run.app` |
| **`BACKEND_API_URL`** | **Swagger UI** URL (`…/docs`). Updated after Deploy API for convenience; not used by the static frontend build. |

Do not point `PUBLIC_API_URL` at `/docs`.

## Dependency auditing (CI)

- **Backend:** `pip-audit` and `bandit` **fail** the workflow on issues.
- **Frontend:** `npm audit --omit=dev --audit-level=high` **fails** CI on production dependencies. Dev-only tools (`serve`, `shadcn` CLI, Playwright) are excluded from that gate.
- Known **transitive** advisories (e.g. Firebase `@grpc/grpc-js`) may be listed in [`.github/npm-audit-allowlist.json`](../.github/npm-audit-allowlist.json) with a review date — remove allowlist entries when upgrades fix them.

## Secret scanning

CI runs **Gitleaks** on repository contents (see [ci.yml](../.github/workflows/ci.yml)) plus a check that forbidden filenames (`.env`, keys, service account JSON) are not tracked.

## Dependency updates

Enable **Dependabot** (or Renovate) on the repository for npm and pip when you want automated update PRs. Not required for the starter baseline.

## Product analytics (PostHog)

Optional. See [setup/posthog.md](setup/posthog.md). When enabled, events are **metadata-only** (no prompts, file contents, or AI text). Session replay is **off** by default. PostHog does not replace Sentry, Cloud Logging, or `ai-evals/`.

## Starter 1.0.0 defaults (documented)

| Choice | Starter default | When to change |
|--------|-----------------|----------------|
| API auth | Open (`AUTH_REQUIRED=false`) | Set `AUTH_REQUIRED` + `NEXT_PUBLIC_AUTH_REQUIRED=true` for login-only demos |
| Cloud Run ingress | `--allow-unauthenticated` | Cloud Run IAM + auth vars for locked-down API |
| PostHog session replay | Off | Enable only after masking review |
| Firebase client rules | Deny all (`frontend/*.rules`) | Never open client Firestore/Storage; use API + Admin SDK |

## Before submission

- [ ] Decide auth policy (`AUTH_REQUIRED` / public API) and note it in your README.
- [ ] Confirm no secrets in git (`gitleaks` green).
- [ ] Firebase rules: CI **deploy-firebase-rules** green after each rules change, or [fallback checklist](setup/firebase-backend.md#fallback-firebase-rules-if-ci-fails).
- [ ] PostHog: rotate project key if it was pasted in chat — see [posthog.md](setup/posthog.md#rotate-a-compromised-key).
- [ ] GitHub **Website** + `BACKEND_API_URL` set — [scripts/set-github-repo-links.sh](../scripts/set-github-repo-links.sh) or Deploy API notice; [github-google-oidc.md](setup/github-google-oidc.md#4-github-repo-links-website--swagger-variable).
