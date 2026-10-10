# Migrate to a new GitHub repository (clean Contributors)

Use this when the old repo has **orphan commits** (e.g. `cursoragent`) that still appear on GitHub’s **Contributors** sidebar. A new repo with **one initial commit under your account** gives a clean public graph. **GCP/Firebase/Cloud Run can stay on the same project** — only GitHub remote and Actions config move.

## What you keep vs redo

| Keep (no change) | Redo on new repo |
|------------------|------------------|
| GCP project, Cloud Run service, Firebase Hosting site | GitHub repo URL, clone path |
| `GEMINI_API_KEY`, WIF/OIDC (same GCP SA) | Actions **Variables** (`PUBLIC_API_URL`, `GCP_PROJECT_ID`, …) |
| Local `backend/.env`, `frontend/.env.local` | GitHub **Secrets** if any |
| Domain / `*.web.app` (same Firebase project) | **About** link + `BACKEND_API_URL` variable |

## 1. Choose a name

Example: `violinadoley/meddocs-hackathon` or `violinadoley/ai-hackathon-starter`.

## 2. Export clean tree (no old git history)

On your Mac, from a clone that has **`feature/meddocs-module-1-ea6e`** (includes MedDocs Module 1):

```bash
cd ~/Projects/ai-hackathon-starter
git fetch origin
git checkout feature/meddocs-module-1-ea6e
git pull

# Or run the helper script from repo root:
./scripts/migrate-to-new-github-repo.sh violinadoley/YOUR_NEW_REPO_NAME
```

The script creates a **new folder** with a single commit authored as **you** (set `git config user.email` first).

## 3. Create the empty repo on GitHub

1. GitHub → **New repository** → name `YOUR_NEW_REPO_NAME` → **no** README/license (empty).
2. In the new folder the script prints:

```bash
git remote add origin git@github.com:violinadoley/YOUR_NEW_REPO_NAME.git
git push -u origin main
```

Use `develop` as default branch if you prefer: after push, **Settings → General → Default branch → `develop`**, then:

```bash
git branch -M develop
git push -u origin develop
```

Match your old workflow (`develop` deploys, `main` stable).

## 4. Copy GitHub Actions configuration

In the **old** repo: **Settings → Secrets and variables → Actions**.

Copy to the **new** repo:

- **Variables:** `GCP_PROJECT_ID`, `GCP_REGION`, `PUBLIC_API_URL`, `BACKEND_API_URL`, `AUTH_REQUIRED`, Firebase `NEXT_PUBLIC_*`, MedDocs `DOCUMENT_AI_*` (if set), etc.
- **Secrets:** same as before (e.g. `GEMINI_API_KEY` if stored as secret, WIF provider if used).

See [security-defaults.md](../security-defaults.md) and [github-google-oidc.md](./github-google-oidc.md).

## 5. Trigger deploy

```bash
git push origin develop   # or main, per your workflows
```

Confirm **Actions** → Deploy API / Deploy Frontend green.

Update README **Live app** link if the Hosting URL unchanged (same Firebase project → same `*.web.app`).

## 6. Archive the old repo

Old repo → **Settings → Danger zone → Archive repository**.

Update local clone:

```bash
cd ~/Projects/ai-hackathon-starter   # or rename folder to match new repo
git remote set-url origin git@github.com:violinadoley/YOUR_NEW_REPO_NAME.git
```

## 7. Prevent `cursoragent` returning

- In **Cursor**, disable **Co-authored-by: Cursor** on commits.
- Merge only commits whose author is **your** GitHub noreply email.
- Avoid long-lived `cursor/*` branches on the submission repo; use `feature/*` from your machine or squash-merge with your identity.

## Optional: omit `.cursor` from the new repo

If you do not want IDE config on GitHub:

```bash
./scripts/migrate-to-new-github-repo.sh violinadoley/YOUR_NEW_REPO_NAME --omit-cursor-config
```

Keep a local copy of `.cursor/` for your own Cursor setup.
