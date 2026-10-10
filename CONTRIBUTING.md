# Contributing

Thank you for helping build this project. We optimize for a small team, clear reviews, and safe deployments.

## Branching

| Branch | Purpose |
|--------|---------|
| `main` | Stable / release-ready (no separate cloud deploy) |
| `develop` | Integration; merges here deploy to Cloud Run |
| `feature/*`, `fix/*`, … | Day-to-day work via PR |

**Rules**

1. Do not commit directly to `main` or `develop` (except documented emergencies).
2. Branch from `develop` for features and fixes.
3. Open a Pull Request into `develop`.
4. Optionally merge `develop` → `main` when you want the stable branch to match what you demoed on Cloud Run.

Example:

```bash
git checkout develop
git pull origin develop
git checkout -b feature/my-change
# work, commit, push
gh pr create --base develop
```

## Git author (submission repos)

Commit and merge under **your GitHub account** (`violinadoley` / your noreply email). Avoid leaving bot or IDE integration accounts as the primary author on `main`/`develop` so the repository **Contributors** list reflects your team.

**Do not** add `Co-authored-by: Cursor <cursoragent@cursor.com>` to commit messages — GitHub lists co-authors as **Contributors**. In Cursor, turn off automatic co-author trailers for commits you push here.

```bash
git config user.name "Your Name"
git config user.email "you@users.noreply.github.com"
```

## Pull requests

Use the [PR template](.github/pull_request_template.md). CI must pass before merge.

## Issues

Every meaningful unit of work should have a GitHub Issue. Suggested board columns:

`Backlog → Ready → In Progress → Code Review → Staging → Done`

Use labels: `frontend`, `backend`, `ai`, `infra`, `security`, `database`, `testing`, `bug`, `documentation`, `P0`, `P1`, `P2`.

Skip heavy process for typos and trivial docs-only fixes.

## Local quality gates

```bash
# Backend
cd backend && pip install -r requirements-dev.txt
ruff check app tests && ruff format --check app tests
mypy app && pytest -q
pytest ../ai-evals/regression -q

# Frontend
cd frontend && npm ci
npm run lint && npm run typecheck && npm run build
npm run test:e2e
```

## Secrets

Never commit API keys, `.env`, service account JSON, or certificates. Use `.env.example` files and GitHub/Google Secret Manager for deployed environments.

## AI changes

Version prompts under `backend/app/ai/prompts/`. Update `ai-evals/` when behavior expectations change. See [docs/evaluation/README.md](docs/evaluation/README.md).

## Code review

- At least one approval from a teammate for non-trivial changes.
- Security-sensitive or schema changes need explicit review.

See also [SECURITY.md](SECURITY.md), [docs/development/workflow.md](docs/development/workflow.md), and GitHub setup:

- [Branch protection](docs/setup/github-branch-protection.md) (`main` / `develop`, required CI checks)
- [Labels and project board](docs/setup/github-labels-and-project.md)
