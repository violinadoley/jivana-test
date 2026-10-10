---
name: mcp-setup-review
description: >-
  Safely configure or verify an approved MCP using the project catalogue.
  Use when the user asks to add, fix, or review MCP configuration—not to
  bulk-install all MCPs.
disable-model-invocation: true
---

# MCP setup review

## Rules

- Read `docs/architecture/mcp-and-tooling-catalogue.md` and `docs/mcp.md`.
- Do not install every MCP; one integration at a time, user-approved.
- Never commit secrets; use OAuth or `${env:VAR}` per `.env.example` and `mcp-safety.mdc`.
- Prefer **dev/staging** GCP/Firebase projects; no production write/delete without explicit approval.
- Do not duplicate servers already in `.cursor/mcp.json`.

## Workflow

1. Confirm which MCP the user wants and why (tie to matrix/catalogue recommendation).
2. Check current `.cursor/mcp.json` and `.cursor/mcp.conditional.example.json`.
3. Verify **official** install docs (vendor URL from catalogue).
4. Document required credentials, OAuth steps, and least-privilege IAM.
5. Propose config diff (URLs/commands only—no tokens).
6. Separate read-only vs write-capable tools; note which need human approval.
7. Guide verification: Cursor Settings → MCP status; smoke prompts from `docs/mcp.md`.
8. Report failures accurately; do not claim connection without user confirmation.
9. Never grant IAM, deploy, or delete resources unless the user explicitly requests that separate step.

## Deliverable

Short report:

**MCP name** | **Official?** | **Config snippet** | **Auth** | **Permissions** | **Read/write** | **Verify steps** | **Risks**
