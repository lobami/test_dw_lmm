#!/usr/bin/env python3
"""Cleanup script for refresh tokens.

Deletes refresh tokens that are revoked or expired. Use --dry-run to preview.
"""
import argparse
from datetime import datetime, timedelta

from app.scripts.cleanup_refresh_tokens import main as _main


if __name__ == '__main__':
    _main()



def cleanup(dry_run: bool = True, older_than_days: int = None):
    db = SessionLocal()
    try:
        q = db.query(user_models.RefreshToken)
        now = datetime.utcnow()
        # Build filters: revoked OR expires_at < now
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

        # Delete tokens
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


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true", default=False)
    p.add_argument("--older-than-days", type=int, help="Only delete tokens created more than this many days ago")
    args = p.parse_args()
    exit(cleanup(dry_run=args.dry_run, older_than_days=args.older_than_days))


if __name__ == '__main__':
    main()
