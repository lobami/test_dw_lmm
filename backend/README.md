# Backend — Campaign Analytics API

Este README cubre instalación, variables de entorno, migraciones, seed, ejecución y checklist para producción del backend.

## Requisitos
- Python 3.9+
- (Opcional) Docker y docker-compose

## Instalación local

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Variables de entorno importantes
- `DATABASE_URL` — URL de la base de datos (ej. `sqlite:///./campaigns.db` o `postgresql://user:pass@db:5432/dbname`)
- `SECRET_KEY` — clave secreta para firmar JWTs
- `FRONTEND_ORIGINS` — lista coma-separada de orígenes permitidos (NO usar `*` en producción)
- `LOG_LEVEL` — nivel de logs (INFO, DEBUG, WARNING)
- `TESTING` — poner a `1` para activar modo testing (usa in-memory DB)
- `ENV` — `production` para activar validaciones de seguridad en arranque

## Migraciones (Alembic)

Aplicar migraciones:

```bash
cd backend
alembic upgrade head
```

En CI se recomienda ejecutar `alembic upgrade head` antes de correr tests.

## Seed (cargas de datos)

El seed está separado de las migraciones. Para cargar los CSVs y crear el admin por defecto:

```bash
cd backend
python seed.py
# o como módulo del paquete
python -m app.seed
```

El seed es idempotente.

## Ejecutar la aplicación (desarrollo)

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Production / Render notes

This repository includes `docker-compose.prod.yml` as a production-like, local example that runs a Postgres service and the backend. When deploying to Render you typically use Render's managed Postgres database and set the `DATABASE_URL` environment variable in the Render dashboard. The compose file is useful to run a production-like stack locally or in a VM.

Example local usage (uses the settings inside `docker-compose.prod.yml`):

```bash
# from backend/
docker-compose -f docker-compose.prod.yml up -d --build

# Follow logs for the backend
docker-compose -f docker-compose.prod.yml logs -f backend
```

DATABASE_URL example

When running locally with the `db` service the matching `DATABASE_URL` looks like:

```
postgresql://postgres:postgres@db:5432/campaigns
```

When deploying to Render you'll get a full connection string in the dashboard. Set that string as the `DATABASE_URL` env var for your service. Example (Render provides a URL similar to):

```
postgres://<user>:<password>@<host>:5432/<dbname>
```

Important: for production make sure `ENV=production`, `SECRET_KEY` is set to a long random value, and `FRONTEND_ORIGINS` lists the allowed origins (do not use `*`).

Backup and restore commands (Postgres)

Below are common commands you can run from a machine that can reach your Postgres instance (replace placeholders). On Render you can run these from your local machine using the connection details Render provides.

# Dump entire DB to a plain SQL file
PGPASSWORD="<password>" pg_dump -h <host> -p 5432 -U <user> -d <dbname> -F p -b -v -f backup.sql

# Dump compressed custom-format archive (recommended for restore with pg_restore)
PGPASSWORD="<password>" pg_dump -h <host> -p 5432 -U <user> -d <dbname> -F c -b -v -f backup.dump

# Restore from custom-format archive
PGPASSWORD="<password>" pg_restore -h <host> -p 5432 -U <user> -d <target_db> -v backup.dump

If you're using the included `docker-compose.prod.yml` you can run the dump from the `db` container:

```bash
# create a dump file from inside the running db container
docker-compose -f docker-compose.prod.yml exec db pg_dump -U postgres -d campaigns -F c -b -v -f /tmp/backup.dump

# copy it out to the host
docker cp $(docker-compose -f docker-compose.prod.yml ps -q db):/tmp/backup.dump ./backup.dump
```

And restore into the local db container:

```bash
docker cp ./backup.dump $(docker-compose -f docker-compose.prod.yml ps -q db):/tmp/backup.dump
docker-compose -f docker-compose.prod.yml exec db pg_restore -U postgres -d campaigns -v /tmp/backup.dump
```

Notes for Render
- Render provides managed Postgres and a connection string you should use as `DATABASE_URL`.
- For scheduled backups you can run the `pg_dump` commands from a CI job or a small scheduled service. Render also offers automated backups for their managed DBs — consult the Render dashboard.

Security checklist (quick reminder)
- Always use TLS (HTTPS) with secure cookies in production.
- Use a strong `SECRET_KEY` and rotate it carefully (rotating will invalidate tokens).
- Do not expose Postgres admin ports publicly; use the connection string Render provides.

Deploying to Render (step-by-step)

1. Push your repo to a Git provider (GitHub/GitLab). Ensure the `backend/Dockerfile` is present at the repository root or in the `backend/` folder and builds the app.

2. Create a new Web Service in Render:
	- Select "Connect a repository" and pick this repo and branch (e.g. `main`).
	- For Environment choose "Docker".
	- Set the build and start commands if you need custom behavior. A minimal start command is:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

3. Add a Managed Postgres Database in Render:
	- In Render dashboard create a new Database (Postgres) with a suitable plan.
	- After creation, Render exposes the connection info. Copy the connection string.

4. Configure environment variables for the Web Service:
	- `DATABASE_URL`: paste the Postgres connection string from the managed DB (example: `postgres://user:pass@hostname:5432/dbname`).
	- `SECRET_KEY`: a long random secret for signing tokens.
	- `ENV`: set to `production`.
	- `FRONTEND_ORIGINS`: your frontend origin(s), e.g. `https://my-frontend.onrender.com` (comma-separated if multiple).
	- Any other secrets (SENTRY_DSN, EMAIL credentials) as needed.

5. Run migrations and seed (one-off / shell):
	- Option A (recommended): Use Render's "Shell" for the service (open a shell in the dashboard) and run:

```bash
# from the service shell
alembic upgrade head
python -m app.seed
```

	- Option B: Add a deploy hook or a small migration job that runs before your web service starts. Avoid running long migrations in the web process on every deploy.

6. Health checks and ports:
	- Render expects your service to bind to the port it provides; this example uses port 8000. Confirm the `startCommand` matches.
	- Configure the health check path to `/health` in the Render service settings so Render knows when the service is healthy.

7. Backups and maintenance:
	- Use Render's automated backups for managed Postgres, or schedule periodic `pg_dump` runs to an external storage.
	- For manual dumps, run `pg_dump` from your local machine or from a Render shell using the DB connection string.

8. Secrets and security:
	- Never commit secrets to repo; use Render secrets.
	- Ensure CORS and cookie policies are set correctly (`allow_credentials=True` and `SameSite=None` + `Secure` when using cross-site cookies over HTTPS).

Example `render.yaml`

This repository includes an example `backend/render.yaml` demonstrating a simple Web Service + managed Postgres entry. It's a starting point; adjust `plan`, `region`, and `env` to your needs.

If you want, I can:
- Add an automated migration job that runs `alembic upgrade head` as a separate Render "cron job"/background job before service startup.
- Create a small deploy script that runs migrations then restarts the web service via the Render API.

Automatic migrations on deploy

Two options are provided so you can choose the workflow that fits your CI/CD process:

1) Container startup runs migrations (idempotent)

	 - The backend Docker image now uses a small entrypoint script that runs
		 `alembic upgrade head` and then starts Uvicorn. This is convenient and
		 makes the container self-migrating, but be aware that long-running
		 migrations may delay service startup.

	 - The Dockerfile already sets the default command to run the startup script.

2) Explicit Render job (recommended for controlled deploys)

	 - `backend/render.yaml` includes a `run-migrations` job example you can run
		 manually from the Render dashboard or invoke from CI before flipping the
		 production service. This is the safest option for production where you want
		 control over when migrations execute.

Choose one: for automated pipelines prefer the Render job (option 2). For
simple deployments or development convenience, the container startup script
(option 1) will run migrations automatically.

Migration job examples (Render)

You can run migrations on Render in several ways. Two common patterns are:

1) One-off job (recommended for controlled deploys)

	 - In the Render dashboard create a new "Job" (or use the `jobs` entry in
		 a `render.yaml`) that runs `alembic upgrade head` in your service image.
	 - Run this job manually from the dashboard or via the Render API after a
		 deploy. This gives you a controlled migration step and avoids long-running
		 migrations inside the web process.

	 Example `render.yaml` snippet (see `backend/render.yaml` in this repo):

```yaml
# jobs:
#  - type: job
#    name: run-migrations
#    env: docker
#    branch: main
#    plan: starter
#    command: alembic upgrade head
```

2) Scheduled / cron job (use sparingly)

	 - You can create a scheduled job (cron) that runs migrations at a maintenance
		 window. Most teams prefer manual or CI-driven migrations to avoid surprises.

	 Example `render.yaml` snippet (commented):

```yaml
# cron_jobs:
#  - name: nightly-migrations
#    schedule: "0 3 * * *" # daily at 03:00 UTC
#    command: alembic upgrade head
#    env: docker
#    branch: main
#    plan: starter
```

Recommended flow

- Add a small migration job and run it manually after deploying (or wire it into
	your CD pipeline as a separate step). Confirm `alembic upgrade head` succeeds
	in a staging environment before running in production.
- Use the Render Shell to run `alembic upgrade head` and `python -m app.seed` for
	one-off tasks when testing.

## Lista obligatoria (elementos a incluir en README / producción)

Por petición, los siguientes puntos deben aparecer en el README y cubrirse antes de poner en producción:

1. Ejecutar/automatizar migraciones en el deploy (paso/Job: `alembic upgrade head`).
2. Indicar y exigir variables de producción: `ENV=production` y `FRONTEND_ORIGINS` (no usar `*`).
3. Documentar y forzar TLS + políticas de cookies/CORS en producción (Secure, SameSite, allow_credentials).
4. Instrucciones y/o automatización de backups y restore (`pg_dump`/`pg_restore`) para producción.
5. Job/cron documentado para limpieza periódica de `refresh_tokens` (housekeeping).
6. Añadir/recordar índices y constraints en DB y agregar migraciones correspondientes (ej. `users.email` único, índice en `refresh_tokens.token`).
7. Tests mínimos documentados/obligatorios (unit/integration) para endpoints críticos y paginación.
8. Completar migración a Pydantic v2 (auditar y actualizar schemas) y reflejarlo en el README.
9. Documentar el flujo de despliegue reproducible (Docker/Compose/Render): cómo configurar secrets (`DATABASE_URL`, `SECRET_KEY`) y ejecutar migraciones/seed en producción.



```

## Endpoints útiles
- `POST /auth/register` — registra usuario
- `POST /auth/token` — login (devuelve access token en JSON y set-cookie refresh httpOnly)
- `POST /auth/refresh` — rota refresh token y devuelve nuevo access token
- `POST /auth/logout` — revoca refresh token y limpia cookie
- `GET /campaigns/` — listado paginado de campañas
- `GET /campaigns/{name}` — detalle de campaña (incluye periods y sites)
- `GET /health` — healthcheck que verifica la conexión a BD
- `GET /metrics` — métricas Prometheus (si `prometheus_client` está instalado)

## Script de limpieza de refresh tokens

Se incluye un script para limpiar refresh tokens expirados o revocados:

```bash
cd backend
python backend/scripts/cleanup_refresh_tokens.py --dry-run
python backend/scripts/cleanup_refresh_tokens.py
```

Puedes crear un cron/job en producción para ejecutarlo periódicamente.

## Docker / docker-compose (ejemplo rápido)

Ejemplo `docker-compose` para desarrollo con Postgres está en `backend/docker-compose.yml` (actualmente el archivo por defecto usa SQLite). Para producción recomendamos:

- Usar un servicio Postgres gestionado o un contenedor Postgres en compose.
- Establecer `DATABASE_URL` con la URL de Postgres.

## Checklist mínima para producción

- Ejecutar `alembic upgrade head` durante deploy
- Asegurar `ENV=production` y `FRONTEND_ORIGINS` con dominios concretos
- Forzar TLS (HTTPS) en front y backend (cookies Secure=True)
- Configurar backups periódicos de la BD
- Configurar job para limpieza de `refresh_tokens` expirados/revocados
- Revisar índices y constraints (ej. unicidad en `users.email`, índice en `refresh_tokens.token`)
- Monitorizar `/health` y `/metrics` y configurar alertas

## Backups y restore (breve)

- Backup Postgres: `pg_dump` al almacenamiento seguro o snapshot del proveedor
- Restore Postgres: `psql` o `pg_restore` según el formato

## Logs y métricas

- El backend emite logs a stdout; si `python-json-logger` está instalado los logs saldrán en JSON (útil para plataformas como Render).
- `LOG_LEVEL` controla el nivel de logs.
- `GET /metrics` expone métricas si `prometheus_client` está instalado.

---

Si quieres, puedo añadir un `docker-compose.prod.yml` de ejemplo con Postgres y mostrar los comandos exactos para backup/restore.
