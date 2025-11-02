#!/usr/bin/env bash
set -euo pipefail

# Run smart migrations that check if they need to be executed
# This prevents duplicate migration conflicts during deployment

echo "🚀 Starting smart migration process..."
python smart_migrations.py

echo "🌐 Starting uvicorn server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
