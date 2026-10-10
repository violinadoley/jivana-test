# Optional MCP setup (local development)

**Not shipped to users.** This is for developers who want IDE-integrated tools (GitHub, GCP, Firebase, etc.) while working on the repo.

Adoption tiers and competition-adjacent Google tools: [architecture/mcp-and-tooling-catalogue.md](architecture/mcp-and-tooling-catalogue.md).

Example config: [`.cursor/mcp.json`](../.cursor/mcp.json) (merge with your editor’s global MCP settings). **Do not commit secrets**—use OAuth or `${env:VAR}` interpolation only.

Official references:

- [Cursor MCP docs](https://cursor.com/docs/context/mcp)
- [Google Cloud MCP overview](https://docs.cloud.google.com/mcp/overview)
- [Google Cloud supported MCP products](https://docs.cloud.google.com/mcp/supported-products)

---

## Required MCPs (configured)

### GitHub

| | |
|---|---|
| **Purpose** | Repositories, issues, PRs, branches, CI visibility |
| **Provider** | GitHub (`github/github-mcp-server`) |
| **Why we use it** | Hackathon repo is on GitHub; agent can inspect PRs and repo state |
| **Config** | `.cursor/mcp.json` → `github` |
| **Transport** | stdio via Docker |
| **Authentication** | **OAuth** (browser login on first use). Alternative: remote server + PAT — see [`.cursor/mcp.github-remote.example.json`](../.cursor/mcp.github-remote.example.json) |
| **Use for** | Read repo metadata, issues, PRs; create issues/PRs when asked |
| **Manual approval** | Merging PRs, deleting branches, changing repo settings |
| **Security** | Do not commit PATs; prefer OAuth Docker image over deprecated `@modelcontextprotocol/server-github` |

Docs: [Install GitHub MCP in Cursor](https://github.com/github/github-mcp-server/blob/main/docs/installation-guides/install-cursor.md)

---

### Context7

| | |
|---|---|
| **Purpose** | Up-to-date docs for libraries (Next.js, FastAPI, Firebase, Gemini, Tailwind, shadcn) |
| **Provider** | Upstash (`@upstash/context7-mcp`) |
| **Config** | `.cursor/mcp.json` → `context7` |
| **Transport** | stdio (`npx`) |
| **Authentication** | Optional `CONTEXT7_API_KEY` via `${env:CONTEXT7_API_KEY}` (higher limits). OAuth setup: `npx ctx7 setup --cursor --mcp` |
| **Use for** | `resolve-library-id`, `query-docs` before implementing APIs |
| **Manual approval** | N/A (read-only docs) |

Docs: [context7.com](https://context7.com/docs/clients/cli)

---

### Playwright

| | |
|---|---|
| **Purpose** | Browser E2E testing of `/`, `/dashboard`, uploads, AI UI |
| **Provider** | Microsoft (`@playwright/mcp`) |
| **Config** | `.cursor/mcp.json` → `playwright` |
| **Transport** | stdio |
| **Authentication** | None |
| **Use for** | Navigate localhost, click, fill forms, screenshots |
| **Manual approval** | Actions that submit real PII or production data |

Docs: [Playwright MCP](https://playwright.dev/docs/getting-started-mcp)

---

### Google Cloud — Resource Manager

| | |
|---|---|
| **Purpose** | Inspect GCP projects, org resources |
| **Provider** | Google Cloud |
| **Endpoint** | `https://cloudresourcemanager.googleapis.com/mcp` |
| **Config** | `.cursor/mcp.json` → `gcp-resource-manager` |
| **Transport** | Remote HTTP |
| **Authentication** | Google OAuth / ADC / IAM — configure in Cursor when prompted ([Authenticate to MCP servers](https://docs.cloud.google.com/mcp/configure-mcp-ai-application)) |
| **Use for** | Confirm project ID, list projects |
| **Manual approval** | Creating/deleting projects, IAM changes |

Enable API: `gcloud services enable cloudresourcemanager.googleapis.com`

---

### Google Cloud — Cloud Run

| | |
|---|---|
| **Purpose** | List services, inspect revisions, deploy backend |
| **Provider** | Google Cloud |
| **Endpoint** | `https://run.googleapis.com/mcp` |
| **Config** | `.cursor/mcp.json` → `gcp-cloud-run` |
| **Transport** | Remote HTTP |
| **Authentication** | Google OAuth / IAM (`roles/mcp.toolUser` recommended) |
| **Use for** | Inspect Cloud Run URL, service config, deployment troubleshooting |
| **Manual approval** | **All deploys**, traffic changes, deleting services |

Docs: [Use the Cloud Run MCP server](https://docs.cloud.google.com/run/docs/use-cloud-run-mcp)

Enable API: `gcloud services enable run.googleapis.com`

---

### Google Cloud — Cloud Storage

| | |
|---|---|
| **Purpose** | Inspect buckets/objects for uploads and Firebase Storage buckets |
| **Provider** | Google Cloud |
| **Endpoint** | `https://storage.googleapis.com/storage/mcp` |
| **Config** | `.cursor/mcp.json` → `gcp-cloud-storage` |
| **Transport** | Remote HTTP |
| **Authentication** | Google OAuth / IAM |
| **Use for** | List buckets/objects, read metadata, debug upload paths |
| **Manual approval** | **delete_object**, **delete_bucket**, **write_text** on production buckets |

Docs: [Use the Cloud Storage MCP server](https://docs.cloud.google.com/storage/docs/use-cloud-storage-mcp)

Enable API: `gcloud services enable storage.googleapis.com`

---

### Google Cloud — Firestore

| | |
|---|---|
| **Purpose** | Inspect/query Firestore documents and collections |
| **Provider** | Google Cloud |
| **Endpoint** | `https://firestore.googleapis.com/mcp` |
| **Config** | `.cursor/mcp.json` → `gcp-firestore` |
| **Transport** | Remote HTTP |
| **Authentication** | Google OAuth / IAM (e.g. `roles/mcp.toolUser`, `roles/datastore.user`) |
| **Use for** | Debug dev database state, list documents |
| **Manual approval** | **delete_document**, **delete_database**, production writes |

Docs: [Use the Firestore MCP server](https://docs.cloud.google.com/firestore/native/docs/use-firestore-mcp)

Enable API: `gcloud services enable firestore.googleapis.com`

---

### Firebase

| | |
|---|---|
| **Purpose** | Firebase init, Hosting, Auth users, Firestore/Storage helpers, project context |
| **Provider** | Google Firebase (`firebase-tools` MCP) |
| **Config** | `.cursor/mcp.json` → `firebase` |
| **Transport** | stdio — `npx firebase-tools@latest mcp` |
| **Authentication** | Same as Firebase CLI (`firebase login` or ADC on Cloud Run dev machines) |
| **Use for** | `firebase_init`, hosting deploy guidance, Firestore queries in active project |
| **Manual approval** | Auth user changes, deploys, destructive Firestore ops |

Docs: [Firebase MCP server](https://firebase.google.com/docs/ai-assistance/mcp-server)

**Note:** Overlaps with remote Firestore MCP—use Firebase MCP for day-to-day hackathon project work.

---

### Sentry

| | |
|---|---|
| **Purpose** | Production error triage, stack traces, issue search |
| **Provider** | Sentry |
| **Endpoint** | `https://mcp.sentry.dev/mcp` (optionally scope: `/mcp/{org}/{project}`) |
| **Config** | `.cursor/mcp.json` → `sentry` |
| **Transport** | Remote HTTP |
| **Authentication** | **OAuth** on first connect in Cursor |
| **Use for** | Search issues, inspect errors after deploy |
| **Manual approval** | Changing issue status, deleting data, exposing user PII |

Docs: [Sentry MCP](https://docs.sentry.io/product/sentry-mcp/)

---

### Postman

| | |
|---|---|
| **Purpose** | Test FastAPI `/health`, `/api/v1/ai/generate`, file upload against local or Cloud Run |
| **Provider** | Postman |
| **Endpoint** | `https://mcp.postman.com/minimal` (see `/code`, `/mcp` for more tools) |
| **Config** | `.cursor/mcp.json` → `postman` |
| **Transport** | Remote HTTP (streamable) |
| **Authentication** | **OAuth** (US server, recommended). Optional: `Authorization: Bearer ${env:POSTMAN_API_KEY}` |
| **Use for** | HTTP request validation, collection-driven API tests |
| **Manual approval** | Running collections against production with real user data |

Docs: [Postman remote MCP server](https://learning.postman.com/docs/developer/postman-api/postman-mcp-server/postman-mcp-remote-server/)

---

## Conditional MCPs (not enabled by default)

Copy entries from [`.cursor/mcp.conditional.example.json`](../.cursor/mcp.conditional.example.json) into `.cursor/mcp.json` only when needed.

| MCP | Endpoint | Enable when |
|-----|----------|-------------|
| BigQuery | `https://bigquery.googleapis.com/mcp` | Large analytics / public datasets |
| Maps Grounding Lite | `https://mapstools.googleapis.com/mcp` | Location / maps / nearby resources |
| Maps Code Assist | `https://mapscodeassist.googleapis.com/mcp` | Maps API development assistance |
| Google Analytics Data | `https://analyticsdata.googleapis.com/mcp/v1` | Product analytics / engagement |
| Figma | `https://mcp.figma.com/mcp` | UI designs drive frontend implementation |
| Hugging Face | `https://huggingface.co/mcp?login` | Hub models/datasets beyond Gemini |

---

## Environment variables (shell / OS — not in `mcp.json`)

Set in your environment (or team password manager), not in committed files:

| Variable | Used by |
|----------|---------|
| `CONTEXT7_API_KEY` | Context7 (optional) |
| `GITHUB_TOKEN` | GitHub remote MCP example only |
| `POSTMAN_API_KEY` | Postman EU or API-key auth |
| `HF_TOKEN` | Hugging Face MCP (if not using OAuth URL) |

See [`.env.example`](../.env.example) for app secrets (Gemini, Firebase)—separate from MCP.

---

## Setup checklist

1. **Restart Cursor** after changing `.cursor/mcp.json`.
2. **Settings → Tools & Integrations → MCP** — check each server status (green = connected).
3. **GitHub:** Docker Desktop running → connect `github` → complete OAuth in browser.
4. **Google Cloud:** `gcloud auth login` and `gcloud config set project YOUR_DEV_PROJECT`; enable APIs listed above; approve OAuth in Cursor for each remote GCP server.
5. **Firebase:** `npm install -g firebase-tools` (optional); `firebase login`; run MCP from repo root with `.firebaserc` configured.
6. **Sentry / Postman / Figma / HF:** complete OAuth when Cursor prompts (first tool use).

---

## Verify MCP status

- **Cursor UI:** Settings → MCP → status indicator per server.
- **MCP Logs:** Command palette → output → MCP Logs (header/auth issues).
- **Smoke tests (after auth):**
  - GitHub: “List my repositories”
  - Context7: query docs for `next.js` App Router
  - Playwright: open `http://localhost:3000`
  - Cloud Run: list services in dev project
  - Postman: minimal server connected (OAuth)

Cursor CLI was not available in this environment; verification is manual in the IDE.

---

## Security summary

- Project [`.cursor/mcp.json`](../.cursor/mcp.json) contains **no plaintext secrets**.
- Use **dev/staging** GCP/Firebase projects for MCP mutations.
- Treat Firestore/Storage **delete** tools as production-sensitive.
- Do not commit service account JSON or PATs.
