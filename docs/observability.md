# Observability

We use **Google Cloud Logging** and **Cloud Run metrics** by default — no paid third-party APM required for the hackathon phase.

## What we log (backend)

- JSON structured logs (`app.core.logging`)
- Request path, method, status, duration (middleware)
- `request_id` when propagated
- `environment`, `APP_VERSION`, `GIT_SHA` at startup and health endpoints
- AI metadata (future): model id, `AI_PROMPT_VERSION`, token/cost estimates — **not** full user prompts in production unless required

## What we do not log

- API keys, bearer tokens, passwords
- Unnecessary PII
- Full document contents by default

## Health checks

| Endpoint | Purpose |
|----------|---------|
| `GET /health` | Liveness — cheap, no AI |
| `GET /ready` | Readiness — extend when dependencies are required |

Cloud Run uses request routing; configure startup probes via Cloud Run health checks when adding dependencies.

## Dashboards (MANUAL)

In GCP Console → **Monitoring**, create dashboards for:

- Cloud Run request count, latency, 5xx rate
- Error log metric filters (`severity>=ERROR`)

## Alerts (optional, MANUAL)

Budget alerts in **Billing → Budgets & alerts** to avoid surprise Gemini or Cloud Run costs.

## Tracing

Not enabled by default. Add OpenTelemetry only if latency debugging requires it.
