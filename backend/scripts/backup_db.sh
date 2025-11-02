#!/usr/bin/env bash
set -euo pipefail

# Backup the Postgres database using pg_dump (custom format).
# Usage:
#   DATABASE_URL=postgres://user:pass@host:5432/dbname BACKUP_DIR=./backups ./backup_db.sh
# Or pass DATABASE_URL as first arg:
#   ./backup_db.sh "postgres://user:pass@host:5432/dbname"

DB_URL="${1:-${DATABASE_URL:-}}"
if [ -z "$DB_URL" ]; then
  echo "ERROR: DATABASE_URL must be provided as env var or first argument." >&2
  exit 2
fi

BACKUP_DIR="${BACKUP_DIR:-./backups}"
mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date -u +"%Y%m%dT%H%M%SZ")
OUTFILE="$BACKUP_DIR/db-backup-$TIMESTAMP.dump"

echo "Creating backup to $OUTFILE..."

if ! command -v pg_dump >/dev/null 2>&1; then
  echo "ERROR: pg_dump not found in PATH. Install postgresql-client package." >&2
  exit 3
fi

# Use custom format (-Fc) for efficient restores with pg_restore
PGPASSWORD="${PGPASSWORD:-}" exec pg_dump --format=custom --file="$OUTFILE" --dbname="$DB_URL"

echo "Backup completed: $OUTFILE"

# Optional: print suggested restore command
echo "To restore: ./restore_db.sh $OUTFILE"
