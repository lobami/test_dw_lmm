"""Cleanup expired or long-revoked refresh tokens.

Usage:
    python -m app.scripts.cleanup_refresh_tokens --help

Defaults:
- Remove tokens whose `expires_at` is older than now (expired) and older than
  `--keep-expired-days` (default 30 days).
- Remove tokens marked `revoked=True` and older than `--keep-revoked-days`
  (default 7 days).

This can be scheduled as a cron job or run as a platform scheduled task.
"""
from datetime import datetime, timedelta
import argparse
import logging

from ...database import SessionLocal
from ..users import models as user_models


logger = logging.getLogger("app.scripts.cleanup_refresh_tokens")


def cleanup(db, keep_expired_days: int = 30, keep_revoked_days: int = 7):
    now = datetime.utcnow()
    expired_cutoff = now - timedelta(days=keep_expired_days)
    revoked_cutoff = now - timedelta(days=keep_revoked_days)

    # Delete expired tokens older than expired_cutoff
    expired_q = db.query(user_models.RefreshToken).filter(user_models.RefreshToken.expires_at < expired_cutoff)
    expired_count = expired_q.count()
    if expired_count:
        logger.info("cleanup_expired_tokens", extra={"deleted": expired_count})
        expired_q.delete(synchronize_session=False)

    # Delete revoked tokens older than revoked_cutoff
    revoked_q = db.query(user_models.RefreshToken).filter(
        user_models.RefreshToken.revoked == True,
        user_models.RefreshToken.created_at < revoked_cutoff,
    )
    revoked_count = revoked_q.count()
    if revoked_count:
        logger.info("cleanup_revoked_tokens", extra={"deleted": revoked_count})
        revoked_q.delete(synchronize_session=False)

    db.commit()
    return expired_count + revoked_count


def main():
    parser = argparse.ArgumentParser(description="Cleanup old refresh tokens")
    parser.add_argument("--keep-expired-days", type=int, default=30,
                        help="Keep expired tokens this many days before deleting (default: 30)")
    parser.add_argument("--keep-revoked-days", type=int, default=7,
                        help="Keep revoked tokens this many days before deleting (default: 7)")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        deleted = cleanup(db, keep_expired_days=args.keep_expired_days, keep_revoked_days=args.keep_revoked_days)
        print(f"Deleted {deleted} refresh tokens")
    finally:
        db.close()


if __name__ == "__main__":
    main()
"""Module wrapper for refresh token cleanup so it can be invoked as
`python -m app.scripts.cleanup_refresh_tokens`.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from typing import Optional

from ..database import SessionLocal
from ..users import models as user_models


def cleanup(dry_run: bool = True, older_than_days: Optional[int] = None) -> int:
    db = SessionLocal()
    try:
        q = db.query(user_models.RefreshToken)
        now = datetime.utcnow()
        tokens = q.filter((user_models.RefreshToken.revoked == True) | (user_models.RefreshToken.expires_at < now)).all()

        if older_than_days is not None:
            cutoff = now - timedelta(days=older_than_days)
            tokens = [t for t in tokens if t.created_at < cutoff]

        print(f"Found {len(tokens)} tokens to remove")
        if dry_run:
            for t in tokens[:100]:
                print(f"DRY: token={t.token} user_id={t.user_id} revoked={t.revoked} expires_at={t.expires_at}")
            if len(tokens) > 100:
                print("... (truncated)")
            return 0

        for t in tokens:
            db.delete(t)
        db.commit()
        print(f"Deleted {len(tokens)} tokens")
        return 0
    except Exception as e:
        print("Error during cleanup:", e)
        db.rollback()
        return 1
    finally:
        db.close()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true", default=False)
    p.add_argument("--older-than-days", type=int, help="Only delete tokens created more than this many days ago")
    args = p.parse_args()
    exit(cleanup(dry_run=args.dry_run, older_than_days=args.older_than_days))


if __name__ == '__main__':
    main()
