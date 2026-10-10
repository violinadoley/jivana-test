#!/usr/bin/env bash
# Deployment stub — see docs/deployment.md for full steps.
set -euo pipefail

echo "Deploy backend to Cloud Run (example):"
echo "  gcloud run deploy ai-hackathon-api \\"
echo "    --source ./backend \\"
echo "    --region YOUR_REGION \\"
echo "    --allow-unauthenticated \\"
echo "    --set-secrets=GEMINI_API_KEY=GEMINI_API_KEY:latest"
echo ""
echo "Deploy frontend (Firebase Hosting / App Hosting):"
echo "  cd frontend && firebase deploy"
echo ""
echo "See docs/deployment.md for complete instructions."
