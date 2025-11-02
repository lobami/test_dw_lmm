# Backups & Restore (Postgres)

This folder contains simple scripts to create and restore Postgres backups used by the project.

Files
- `backup_db.sh` - create a backup using `pg_dump -Fc` (custom format). Writes files to `BACKUP_DIR` (default `./backups`).
- `restore_db.sh` - restore a backup created by `backup_db.sh` using `pg_restore`.
- `../app/scripts/backup.py` - a tiny Python wrapper so you can run the backup as a Python module

Basic usage

Create a backup (example):

```bash
DATABASE_URL=postgres://user:pass@host:5432/dbname BACKUP_DIR=./backups ./backup_db.sh
```

Restore a backup to a target DB (example):

```bash
./restore_db.sh ./backups/db-backup-20250101T120000Z.dump "postgres://user:pass@host:5432/targetdb"
```

Cron / scheduler example

To run nightly backups, you can schedule a cronjob on a host that has access to the DB and `pg_dump`.

Example crontab (run daily at 02:00 UTC):

```
# m h dom mon dow command
0 2 * * * cd /srv/app/backend/scripts && DATABASE_URL=${DATABASE_URL} BACKUP_DIR=/var/backups/myapp ./backup_db.sh >/var/log/backup_db.log 2>&1
```

Retention

Keep a retention policy by deleting old backups. Example: keep last 30 days.

```bash
find /var/backups/myapp -type f -name 'db-backup-*.dump' -mtime +30 -delete
```

Running inside Docker

If you prefer running the backup from the project container image:

```bash
docker run --rm \
  -e DATABASE_URL="${DATABASE_URL}" \
  -v /var/backups/myapp:/backups \
  your-backend-image:latest \
  /app/scripts/backup_db.sh
```

Security

- Prefer injecting DB credentials via secure platform secrets rather than hardcoding.
- If using `PGPASSWORD` environment variable, be careful with process lists and logs.
