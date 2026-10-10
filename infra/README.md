# Infrastructure

This repository does **not** use Terraform by default (team size and hackathon scope).

## What lives here

- Documentation pointers for GCP/Firebase resources
- Future: optional Terraform modules if the team outgrows manual setup

## Resource naming (convention)

| Resource | Name |
|----------|------|
| Cloud Run API | `ai-hackathon-api` |
| Docker image | `ai-hackathon-api:$GIT_SHA` |
| Artifact Registry repo | `ai-hackathon` |

Replace `ai-hackathon` prefix when you rename the product.

## Setup

All cloud provisioning steps are **MANUAL SETUP REQUIRED**. Start with [docs/setup/github-google-oidc.md](../docs/setup/github-google-oidc.md).
