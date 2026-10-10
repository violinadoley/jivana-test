# AI evaluation framework

First-class regression testing for prompts, models, and retrieval changes.

## Status

**Framework + MedDocs manifest** — generic prompt tests remain; `datasets/meddocs/manifest.json` holds synthetic reconciliation gold labels (no live Gemini in default CI).

## Layout

| Path | Purpose |
|------|---------|
| `datasets/` | Versioned JSONL/JSON test cases (no production PII) |
| `evaluators/` | Scoring functions (groundedness, schema validity, etc.) |
| `regression/` | Pytest entrypoints wired into CI when AI paths change |
| `results/` | Gitignored local/CI artifacts (`.gitkeep` only in repo) |

## Running locally

```bash
cd backend
pip install -r requirements-dev.txt
pytest ../ai-evals/regression -q
```

## When to run

- Any PR that changes `backend/app/ai/**`, prompts, model config, or retrieval
- Before promoting `develop` → `main`

## TODO (product team)

- [ ] Define golden Q&A dataset for your problem domain
- [ ] Add groundedness/faithfulness checks against retrieved context
- [ ] Add structured-output schema validation tests
- [ ] Add latency/cost budgets per eval case
- [ ] Wire live Gemini calls only in scheduled/staging jobs (not every PR) if cost is a concern

## Regression policy

A change to `AI_PROMPT_VERSION`, `GEMINI_MODEL`, or retrieval configuration must:

1. Bump version metadata
2. Update or add eval cases
3. Run `ai-evals/regression` in CI
