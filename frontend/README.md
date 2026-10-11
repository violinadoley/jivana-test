# JIVANA frontend

Next.js App Router app (static export) for Firebase Hosting.

## Commands

```bash
npm ci
cp .env.local.example .env.local   # set NEXT_PUBLIC_API_URL
npm run dev          # http://localhost:3000
npm run build        # output in out/
npm run lint && npm run typecheck
npm run test:e2e     # local Playwright (starts preview server)
npm run test:e2e:deployed   # smoke against .web.app
```

## Key routes

| Route | Purpose |
|-------|---------|
| `/` | Marketing home |
| `/dashboard` | Hybrid workspace (med rec + enterprise tabs) |
| `/smart/launch` | SMART on FHIR landing |

## Configuration

See [../docs/development/environment-variables.md](../docs/development/environment-variables.md) and `.env.local.example`.

**Full onboarding:** [../docs/development/team-onboarding.md](../docs/development/team-onboarding.md)
