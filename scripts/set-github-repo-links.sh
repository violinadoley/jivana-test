#!/usr/bin/env bash
# Set GitHub repo Website link and BACKEND_API_URL variable (requires gh auth login).
# GITHUB_TOKEN in Actions often cannot patch repo metadata / variables (403).
set -euo pipefail

REPO="${GITHUB_REPOSITORY:-$(gh repo view --json nameWithOwner -q .nameWithOwner)}"
HOMEPAGE="${1:-}"
API_DOCS="${2:-}"

if [[ -z "$HOMEPAGE" || -z "$API_DOCS" ]]; then
  echo "Usage: $0 <homepage_url> <api_swagger_url>" >&2
  echo "Example: $0 https://my-project.web.app https://ai-hackathon-api-xxx.run.app/docs" >&2
  exit 1
fi

gh repo edit "$REPO" \
  --homepage "$HOMEPAGE" \
  --description "Google-native AI hackathon starter (v1.0.0) — Next.js, FastAPI, Gemini, Firebase."

gh variable set BACKEND_API_URL --body "$API_DOCS" --repo "$REPO"

echo "Updated $REPO homepage and BACKEND_API_URL."
