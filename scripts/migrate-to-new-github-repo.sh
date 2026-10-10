#!/usr/bin/env bash
# Export current HEAD as a fresh git repo (single commit, no history).
# Usage: ./scripts/migrate-to-new-github-repo.sh violinadoley/NEW_REPO_NAME [--omit-cursor-config]
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 GITHUB_SLUG [--omit-cursor-config]" >&2
  echo "Example: $0 violinadoley/meddocs-hackathon" >&2
  exit 1
fi

SLUG="$1"
OMIT_CURSOR=false
if [[ "${2:-}" == "--omit-cursor-config" ]]; then
  OMIT_CURSOR=true
fi

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NAME="${SLUG##*/}"
DEST="${HOME}/Projects/${NAME}-clean-export"

if [[ -d "$DEST" ]]; then
  echo "Remove or rename existing: $DEST" >&2
  exit 1
fi

mkdir -p "$DEST"
git -C "$REPO_ROOT" archive HEAD | tar -x -C "$DEST"

if $OMIT_CURSOR; then
  rm -rf "$DEST/.cursor"
fi

cd "$DEST"
git init -b main
git add -A

if ! git config user.email >/dev/null; then
  echo "Set git identity first, e.g.:" >&2
  echo '  git config --global user.name "Violina Doley"' >&2
  echo '  git config --global user.email "97302655+violinadoley@users.noreply.github.com"' >&2
  exit 1
fi

git commit -m "Initial commit: AI hackathon starter with MedDocs Module 1

Synthetic med reconciliation prototype, FastAPI + Next.js, CI and deploy workflows.
Single clean history for submission (no third-party bot authors)."

echo ""
echo "Created: $DEST"
echo "Author: $(git log -1 --format='%an <%ae>')"
echo ""
echo "Next:"
echo "  1. Create empty repo on GitHub: https://github.com/new  name: ${NAME}"
echo "  2. cd $DEST"
echo "  3. git remote add origin git@github.com:${SLUG}.git"
echo "  4. git push -u origin main"
echo "     (optional: git branch -M develop && git push -u origin develop)"
echo "  5. Copy Actions variables/secrets from old repo; see docs/setup/migrate-new-github-repo.md"
