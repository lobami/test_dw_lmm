#!/usr/bin/env bash
set -euo pipefail

# Run DB migrations, then start the app. This script is safe to run multiple times
# because Alembic upgrades are idempotent.

echo "Running alembic migrations..."
alembic upgrade head

echo "Starting uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
