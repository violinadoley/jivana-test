# GitHub branch protection (`main` + `develop`)

**Status: AUTOMATED** for [violinadoley/project](https://github.com/violinadoley/project) (public repo).

Both **`main`** and **`develop`** require:

- A **pull request** before merge (0 approvals configured — solo-friendly; raise to 1 on `main` when you add teammates)
- **Strict** required status checks: `backend`, `frontend`, `ai-evals`, `e2e`, `secret-scan`
- No force-push or branch deletion

Admins can bypass (`enforce_admins: false`) so you can still unbreak the repo in an emergency.

Previously, **private repos on GitHub Free** could not use branch protection until Pro or public.

---

## Required CI check names

When configuring **Require status checks**, search for and require these job names from the **CI** workflow:

| Check name | Job |
|------------|-----|
| `backend` | Lint, types, tests, pip-audit, bandit |
| `frontend` | Lint, typecheck, build |
| `ai-evals` | AI regression framework |
| `e2e` | Playwright |
| `secret-scan` | Tracked secret filename guard |

Do **not** require `deploy` (Deploy API workflow) on PRs unless you add a dedicated PR check.

Optional: require the workflow-level check **CI** if your plan shows a single aggregated check instead of per-job names.

---

## UI steps (after Pro or public repo)

Repeat for **`main`** and **`develop`**.

1. Open **https://github.com/violinadoley/project/settings/branches**
2. **Add branch protection rule** (or **Add rule**)
3. **Branch name pattern:** `main` (then repeat for `develop`)
4. Enable:
   - **Require a pull request before merging**
     - Optional: require 1 approval (recommended for `main`)
   - **Require status checks to pass before merging**
     - **Require branches to be up to date before merging** (recommended)
     - Search and select: `backend`, `frontend`, `ai-evals`, `e2e`, `secret-scan`
   - **Do not allow bypassing the above settings** (recommended for `main`)
5. **Do not** enable “Restrict who can push” unless you know you need it (can lock out solo dev).
6. Save changes.

### Suggested differences

| Setting | `main` | `develop` |
|---------|--------|-----------|
| Require PR | Yes | Yes |
| Required approvals | 1 (if team > 1) | 0–1 |
| Required status checks | All CI jobs above | Same |
| Allow admin bypass | Off | Optional on for solo hackathon |

---

## Rulesets (alternative, Pro / public)

**Settings → Rules → Rulesets → New ruleset → Target: `main` or `develop`**

Same requirements: pull request + required checks listed above.

---

## Verify

1. Create a test branch, open PR to `develop`, confirm merge is blocked until CI is green.
2. Confirm direct push to `main` is rejected (if rule applies to admins).

---

## Labels & project board

Labels: see [github-labels-and-project.md](./github-labels-and-project.md).
