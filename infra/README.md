# Infrastructure

This repository does **not** use Terraform by default (operational simplicity).

## What lives here

- Documentation pointers for GCP/Firebase resources
- Future: optional Terraform modules if the team outgrows manual setup

## Resource naming (convention)

| Resource | Name |
|----------|------|
| Cloud Run API | `ai-hackathon-api` |
| Docker image | `ai-hackathon-api:$GIT_SHA` |
| Artifact Registry repo | `ai-hackathon` |

GCP resource names keep the **`ai-hackathon-*`** prefix for compatibility with existing deploys; the product brand is **JIVANA**.

## Setup

All cloud provisioning steps are **MANUAL SETUP REQUIRED**. Start with [docs/setup/github-google-oidc.md](../docs/setup/github-google-oidc.md).
