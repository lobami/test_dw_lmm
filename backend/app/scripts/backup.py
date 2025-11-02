"""Simple backup helper to run pg_dump from Python.

This module provides a small programmatic wrapper around the shell scripts so
platforms that prefer python entrypoints can call it as a module:

    python -m app.scripts.backup --out-dir ./backups

It looks for DATABASE_URL in the environment if not passed explicitly.
"""
import argparse
import os
import shlex
import subprocess
from datetime import datetime


def run_backup(database_url: str, out_dir: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    out_file = os.path.join(out_dir, f"db-backup-{ts}.dump")
    cmd = ["pg_dump", "--format=custom", "--file", out_file, "--dbname", database_url]
    subprocess.check_call(cmd)
    return out_file


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--database-url", help="Postgres DATABASE_URL (overrides env DATABASE_URL)")
    parser.add_argument("--out-dir", default="./backups", help="Directory to write backup files")
    args = parser.parse_args()
    db = args.database_url or os.environ.get("DATABASE_URL")
    if not db:
        raise SystemExit("DATABASE_URL must be provided via --database-url or environment variable")
    out = run_backup(db, args.out_dir)
    print(f"Backup completed: {out}")


if __name__ == "__main__":
    main()
