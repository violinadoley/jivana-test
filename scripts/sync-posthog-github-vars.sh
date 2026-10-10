#!/usr/bin/env bash
# Set PostHog GitHub Actions variables for frontend deploy (see docs/setup/posthog.md).
set -euo pipefail

REPO="${GITHUB_REPO:-violinadoley/project}"
KEY="${NEXT_PUBLIC_POSTHOG_KEY:-${1:-}}"
HOST="${NEXT_PUBLIC_POSTHOG_HOST:-https://us.i.posthog.com}"

if [ -z "$KEY" ]; then
  echo "Usage: NEXT_PUBLIC_POSTHOG_KEY=phc_... $0"
  echo "   or: $0 phc_your_project_api_key"
  exit 1
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "Install GitHub CLI (gh) first."
  exit 1
fi

gh variable set NEXT_PUBLIC_POSTHOG_KEY --body "$KEY" --repo "$REPO"
gh variable set NEXT_PUBLIC_POSTHOG_HOST --body "$HOST" --repo "$REPO"
gh variable set NEXT_PUBLIC_POSTHOG_ENABLED --body "true" --repo "$REPO"
gh variable set NEXT_PUBLIC_POSTHOG_SESSION_REPLAY --body "false" --repo "$REPO"

echo "PostHog GitHub variables updated for $REPO. Redeploy frontend (push to develop or workflow_dispatch)."
