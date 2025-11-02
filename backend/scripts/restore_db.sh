#!/usr/bin/env bash
set -euo pipefail

# Restore a Postgres backup created with pg_dump -Fc
# Usage:
#   ./restore_db.sh /path/to/backup.dump "postgres://user:pass@host:5432/dbname"
# Or set DATABASE_URL env var and run:
#   DATABASE_URL=postgres://user:pass@host:5432/dbname ./restore_db.sh /path/to/backup.dump

BACKUP_FILE="${1:-}"
DB_URL="${2:-${DATABASE_URL:-}}"

if [ -z "$BACKUP_FILE" ]; then
  echo "ERROR: path to backup file is required as first argument." >&2
  exit 2
fi
if [ ! -f "$BACKUP_FILE" ]; then
  echo "ERROR: backup file '$BACKUP_FILE' not found." >&2
  exit 3
fi
if [ -z "$DB_URL" ]; then
  echo "ERROR: target DATABASE_URL must be provided as second arg or env var." >&2
  exit 4
fi

if ! command -v pg_restore >/dev/null 2>&1; then
  echo "ERROR: pg_restore not found in PATH. Install postgresql-client package." >&2
  exit 5
fi

echo "Restoring $BACKUP_FILE to $DB_URL (this will create/replace objects in target DB)..."

# Use --clean and --if-exists to remove existing objects before recreating
PGPASSWORD="${PGPASSWORD:-}" exec pg_restore --dbname="$DB_URL" --clean --if-exists "$BACKUP_FILE"

echo "Restore completed."
