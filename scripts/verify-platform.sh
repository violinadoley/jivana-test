#!/usr/bin/env bash
# Platform readiness against a running API. Usage: API_BASE_URL=https://... ./scripts/verify-platform.sh [--probe]
set -euo pipefail

BASE="${API_BASE_URL:-http://127.0.0.1:8000}"
BASE="${BASE%/}"
PROBE="false"
if [ "${1:-}" = "--probe" ]; then
  PROBE="true"
fi

echo "GET ${BASE}/api/v1/platform/capabilities"
caps=$(curl -fsS "${BASE}/api/v1/platform/capabilities")
echo "$caps" | grep -q '"capabilities"'

path="/api/v1/platform/demo-readiness"
if [ "$PROBE" = "true" ]; then
  path="${path}?probe=true"
fi
echo "GET ${BASE}${path}"
ready=$(curl -fsS "${BASE}${path}")
echo "$ready" | grep -q '"core_demo_ready"'

if echo "$ready" | grep -q '"core_demo_ready"[[:space:]]*:[[:space:]]*false'; then
  echo "WARNING: core_demo_ready is false — check GEMINI_API_KEY or Vertex on Cloud Run."
  exit 1
fi

echo "Platform verification passed (probe=${PROBE})."
