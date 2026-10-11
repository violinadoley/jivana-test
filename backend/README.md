# JIVANA backend

FastAPI application deployed to Cloud Run as **`ai-hackathon-api`**.

## Commands

```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
uvicorn app.main:app --reload --reload-dir app --port 8000
```

- Health: http://127.0.0.1:8000/health  
- OpenAPI: http://127.0.0.1:8000/docs  

## Layout

| Path | Purpose |
|------|---------|
| `app/api/routes/` | HTTP routes |
| `app/services/` | Domain logic (documents, search, healthcare, firebase, …) |
| `app/ai/` | Prompts, Gemini service, **Google ADK** agents |
| `tests/` | pytest |

## Configuration

See [../docs/development/environment-variables.md](../docs/development/environment-variables.md) and `.env.example`.
