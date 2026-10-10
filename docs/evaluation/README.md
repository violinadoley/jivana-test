# AI evaluation (CI)

See the runnable framework in [`../../ai-evals/README.md`](../../ai-evals/README.md).

## When CI runs evals

The `ai-evals` job in CI runs on every pull request and on pushes to `main` / `develop`. Today it validates:

- Prompt templates load and render
- Sample dataset JSON integrity
- Structured output schema helpers

## Regression policy

Changing any of the following requires updating eval cases:

- Files under `backend/app/ai/prompts/`
- `GEMINI_MODEL`, `AI_PROMPT_VERSION`
- Retrieval configuration (when added)

## Future metrics

Plan to add scorers for groundedness, tool-call correctness, latency budgets, and cost estimates — without hard-coded fake scores.
