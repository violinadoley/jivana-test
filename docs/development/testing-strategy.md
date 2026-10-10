# Testing strategy

## Pyramid

```text
        ┌─────────────┐
        │  E2E (few)  │  Playwright — landing, dashboard, critical flows
        ├─────────────┤
        │ Integration │  FastAPI TestClient, service boundaries
        ├─────────────┤
        │ AI evals    │  ai-evals/ regression + future golden sets
        ├─────────────┤
        │ Unit (many) │  pytest, pure functions, validators
        └─────────────┘
```

## Backend

- **Location:** `backend/tests/`
- **Run:** `pytest -q` with `GEMINI_API_KEY` set to a dummy value for mocked AI tests
- **Tools:** pytest, TestClient, mocks for Gemini

## AI evaluation

- **Location:** `ai-evals/`
- **Run:** `pytest ai-evals/regression -q` with `PYTHONPATH=backend`
- Expand datasets before changing prompts in production

## Frontend

- **Lint / types:** ESLint, `tsc`
- **E2E:** `npm run test:e2e` (Playwright)

## CI

All of the above run in `.github/workflows/ci.yml` on pull requests and pushes to `main` / `develop`.

## Data policy

Tests must not use production Firestore or real user data. Use fixtures and emulators.
