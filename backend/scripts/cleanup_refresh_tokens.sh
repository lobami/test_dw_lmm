#!/usr/bin/env bash
set -euo pipefail

# Wrapper to run the cleanup script using the installed Python environment in the repo.
# Usage:
#   ./cleanup_refresh_tokens.sh
# Optional env vars:
#   KEEP_EXPIRED_DAYS=30
#   KEEP_REVOKED_DAYS=7

KEEP_EXPIRED_DAYS="${KEEP_EXPIRED_DAYS:-30}"
KEEP_REVOKED_DAYS="${KEEP_REVOKED_DAYS:-7}"

echo "Running refresh_tokens cleanup (keep_expired_days=$KEEP_EXPIRED_DAYS, keep_revoked_days=$KEEP_REVOKED_DAYS)"

python -m app.scripts.cleanup_refresh_tokens --keep-expired-days "$KEEP_EXPIRED_DAYS" --keep-revoked-days "$KEEP_REVOKED_DAYS"
