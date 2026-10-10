## Summary

<!-- What does this PR do? -->

## Problem being solved

<!-- Link GitHub issue: Fixes # -->

## Changes made

-

## Testing performed

- [ ] `cd backend && pip install -r requirements-dev.txt && pytest -q`
- [ ] `cd backend && ruff check app tests && mypy app`
- [ ] `cd frontend && npm ci && npm run lint && npm run typecheck && npm run build`
- [ ] `cd frontend && npm run test:e2e` (if UI flows changed)

## AI / model changes

- [ ] N/A
- [ ] Prompt version bumped (`AI_PROMPT_VERSION` / files under `backend/app/ai/prompts/`)
- [ ] Model or generation config changed
- [ ] `ai-evals/` updated and regression run

## Prompt changes

<!-- List prompt files and rationale -->

## Retrieval changes

<!-- N/A or describe index / chunk / ranking changes -->

## Database / schema changes

<!-- N/A or link runbook steps -->

## Security considerations

<!-- Auth, secrets, PII logging, new dependencies -->

## Performance / cost considerations

<!-- Cloud Run scaling, Gemini calls, Firestore reads -->

## Deployment considerations

<!-- Env vars, migrations, manual GCP steps -->

## Screenshots

<!-- If UI changed -->

## Checklist

- [ ] Squash merge message has **no** `Co-authored-by: Cursor` line
- [ ] Tests pass locally / CI green
- [ ] Lint and type checking pass
- [ ] No secrets committed (`.env`, keys, JSON credentials)
- [ ] Documentation updated if behavior or architecture changed
- [ ] AI evaluation run if AI behavior changed
- [ ] Database changes reviewed (Cloud Run / Firebase project first)
- [ ] Security implications reviewed
- [ ] Cost implications considered
