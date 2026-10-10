#!/usr/bin/env bash
# Smoke-test deployed API. Usage: API_BASE_URL=https://... ./scripts/smoke-api.sh
set -euo pipefail

BASE="${API_BASE_URL:-}"
if [ -z "$BASE" ]; then
  echo "API_BASE_URL is required"
  exit 1
fi

BASE="${BASE%/}"

echo "Checking GET ${BASE}/health"
body=$(curl -fsS "${BASE}/health")
echo "$body" | grep -q '"status"[[:space:]]*:[[:space:]]*"ok"'

echo "Checking GET ${BASE}/ready"
body=$(curl -fsS "${BASE}/ready")
echo "$body" | grep -q '"status"[[:space:]]*:[[:space:]]*"ready"'

echo "Smoke tests passed."
