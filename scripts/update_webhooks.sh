#!/usr/bin/env bash
# Update GitHub webhooks from localhost to production URL
# Usage: PRODUCTION_URL=https://assert-review.vercel.app ./scripts/update_webhooks.sh

set -euo pipefail

PROD_URL="${PRODUCTION_URL:-https://assert-review.vercel.app}"
WEBHOOK_URL="${PROD_URL}/api/webhooks/github"

echo "Updating webhooks to: ${WEBHOOK_URL}"

# List all repos with webhooks and update them
# Usage requires GITHUB_TOKEN with repo write access
if [[ -z "${GITHUB_TOKEN:-}" ]]; then
  echo "Error: GITHUB_TOKEN not set"
  exit 1
fi

# Get repos for authenticated user
REPOS=$(gh api /user/repos --jq '.[].full_name' 2>/dev/null || echo "")

for REPO in $REPOS; do
  HOOKS=$(gh api "/repos/${REPO}/hooks" 2>/dev/null || echo "[]")
  HOOK_ID=$(echo "$HOOKS" | python3 -c "
import json, sys
hooks = json.load(sys.stdin)
for h in hooks:
    if 'localhost' in h.get('config', {}).get('url', '') or 'assert-review' in h.get('config', {}).get('url', ''):
        print(h['id'])
        break
" 2>/dev/null || echo "")
  
  if [[ -n "$HOOK_ID" ]]; then
    echo "Updating hook $HOOK_ID in $REPO..."
    gh api "/repos/${REPO}/hooks/${HOOK_ID}" \
      --method PATCH \
      --field "config[url]=${WEBHOOK_URL}" \
      --field "active=true" > /dev/null
    echo "  Updated: $REPO"
  fi
done

echo "Done."
