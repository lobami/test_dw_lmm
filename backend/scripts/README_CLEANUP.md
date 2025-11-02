# Refresh tokens cleanup

Use the provided scripts to periodically remove expired or long-revoked refresh tokens from the database.

Files
- `cleanup_refresh_tokens.sh` - shell wrapper to run the cleanup job (calls `python -m app.scripts.cleanup_refresh_tokens`).
- `app/scripts/cleanup_refresh_tokens.py` - Python module that performs the cleanup via SQLAlchemy session.

Cron example (daily at 03:00 UTC):

```
0 3 * * * cd /srv/app/backend && ./scripts/cleanup_refresh_tokens.sh >> /var/log/cleanup_refresh_tokens.log 2>&1
```

Platform scheduled job (example for Render): configure a scheduled job that runs the container and executes:

```
/app/scripts/cleanup_refresh_tokens.sh
```

Notes:
- Tune `KEEP_EXPIRED_DAYS` and `KEEP_REVOKED_DAYS` according to retention policy.
- This job should run with application DB credentials (via secure environment variables).
