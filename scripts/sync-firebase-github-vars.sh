#!/usr/bin/env bash
# Sync Firebase web app config into GitHub Actions variables.
# Requires: gh CLI, firebase-tools (npx), firebase login, and a WEB app on the project.
set -euo pipefail

PROJECT_ID="${1:-}"
REPO="${GITHUB_REPO:-violinadoley/project}"

if [ -z "$PROJECT_ID" ]; then
  echo "Usage: $0 YOUR_GCP_PROJECT_ID"
  exit 1
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "Install GitHub CLI (gh) first."
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "Install jq first."
  exit 1
fi

SDK_JSON="$(npx --yes firebase-tools@14.14.0 apps:sdkconfig WEB --project "$PROJECT_ID" | tail -n +1)"
API_KEY="$(echo "$SDK_JSON" | jq -r '.apiKey // empty')"
APP_ID="$(echo "$SDK_JSON" | jq -r '.appId // empty')"
MSG_ID="$(echo "$SDK_JSON" | jq -r '.messagingSenderId // empty')"
STORAGE="$(echo "$SDK_JSON" | jq -r '.storageBucket // empty')"

if [ -z "$API_KEY" ] || [ -z "$APP_ID" ]; then
  echo "Could not parse SDK config. Create a Web app in Firebase console first."
  exit 1
fi

gh variable set NEXT_PUBLIC_FIREBASE_API_KEY --body "$API_KEY" --repo "$REPO"
gh variable set NEXT_PUBLIC_FIREBASE_APP_ID --body "$APP_ID" --repo "$REPO"
gh variable set NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID --body "$MSG_ID" --repo "$REPO"
if [ -n "$STORAGE" ]; then
  gh variable set FIREBASE_STORAGE_BUCKET --body "$STORAGE" --repo "$REPO"
fi

echo "GitHub variables updated for $REPO (auth domain / project id are derived in deploy workflow)."
