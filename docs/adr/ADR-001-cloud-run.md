# ADR-001: Backend on Cloud Run

## Context

We need a managed, low-ops HTTP host for FastAPI with scale-to-zero for hackathon cost control.

## Decision

Deploy the API as a container on **Google Cloud Run** (`ai-hackathon-api` in the hackathon GCP project).

## Alternatives considered

- GKE — too heavy for a 2–4 person team
- Compute Engine VMs — more ops burden
- Cloud Functions — awkward for long-lived FastAPI apps

## Consequences

- Docker image required; Artifact Registry for CI pushes
- Cold starts acceptable for demos; tune min instances only if needed
