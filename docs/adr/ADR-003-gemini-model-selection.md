# ADR-003: Gemini via google-genai SDK

## Context

We need a capable default model with official Google SDK support and env-driven configuration.

## Decision

Use **`google-genai`** with default model **`gemini-2.5-flash`** (override via `GEMINI_MODEL`).

## Alternatives considered

- Vertex-only SDK — more setup for hackathon timeline
- Multiple providers — out of scope for starter

## Consequences

- API keys in Secret Manager for deployed envs
- Prompt versioning under `backend/app/ai/prompts/`
