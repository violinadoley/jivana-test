#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "AI Hackathon Starter — local development"
echo ""
echo "Terminal 1 — Backend:"
echo "  cd \"$ROOT/backend\""
echo "  python -m venv .venv && source .venv/bin/activate"
echo "  pip install -r requirements.txt"
echo "  cp -n .env.example .env 2>/dev/null || true"
echo "  uvicorn app.main:app --reload --port 8000"
echo ""
echo "Terminal 2 — Frontend:"
echo "  cd \"$ROOT/frontend\""
echo "  npm install"
echo "  cp -n .env.local.example .env.local 2>/dev/null || true"
echo "  npm run dev"
echo ""
echo "Optional — Backend via Docker:"
echo "  cd \"$ROOT\" && docker compose up --build backend"
