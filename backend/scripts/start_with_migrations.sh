#!/usr/bin/env bash
set -euo pipefail

# Run smart migrations that check if they need to be executed
# This prevents duplicate migration conflicts during deployment

echo "🚀 Starting migration process..."

# First run standard alembic migrations
echo "📦 Running alembic upgrade head..."
alembic upgrade head

# Then run smart migrations for additional checks
echo "🧠 Running smart migrations..."
python smart_migrations.py

echo "🌐 Starting uvicorn server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
