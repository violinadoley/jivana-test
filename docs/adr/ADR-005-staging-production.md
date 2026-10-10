# ADR-005: Deployed vs local environments (hackathon)

## Context

Full staging + production isolation is valuable for long-lived products but heavy for a hackathon.

## Decision

- **Local** — development on localhost with dev keys and emulators when possible.
- **Cloud** — one GCP project; Cloud Run service `ai-hackathon-api`; deploy from **`develop`** only.
- **`main`** — stable branch and CI target; no second Cloud Run environment in this starter.

Secrets and Firebase data stay in the hackathon GCP project; do not reuse personal or employer production projects.

## Consequences

- Simpler setup (one WIF pool, one set of GitHub variables, GitHub environment `gcp`)
- Less blast-radius separation than multi-env prod — acceptable for competition scope
