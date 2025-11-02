# Flujo de despliegue reproducible (Docker / Compose / Run migrations)

Este archivo documenta un flujo reproducible para desplegar la API en un entorno que soporta contenedores (Docker) o servicios gestionados (Render, Heroku, etc.). No modifica el `README.md` raíz.

Requisitos mínimos de entorno
----------------------------
- `DATABASE_URL` — cadena de conexión Postgres (ej: `postgresql://user:pass@host:5432/dbname`).
- `SECRET_KEY` — secreto para la firma de JWT.
- `FRONTEND_ORIGINS` — orígenes permitidos en producción (ej: `https://app.example.com`).
- `ENV=production` — obliga comprobaciones de seguridad en el arranque.

Archivos relevantes
-------------------
- `docker-compose.prod.yml` — ejemplo de archivo Compose para ejecutar localmente un servicio Postgres + contenedor backend.
- `scripts/start_with_migrations.sh` — entrypoint que ejecuta `alembic upgrade head` y luego arranca `uvicorn`.
- `scripts/backup_db.sh` / `scripts/restore_db.sh` — scripts para backup/restore.
- `app/scripts/backup.py` — wrapper python para backups.

Flujo recomendado (Docker Compose local - producción equivalente a una instancia con env vars)
--------------------------------------------------------------------------------------
1. Configura variables de entorno en un fichero `.env` (no lo subas al repo) o en tu plataforma de despliegue.

   Ejemplo `.env` local (NO COMMIT):

   ```env
   DATABASE_URL=postgresql://postgres:postgres@db:5432/campaigns
   SECRET_KEY=replace-with-strong-secret
   FRONTEND_ORIGINS=http://localhost:5173
   ENV=production
   LOG_LEVEL=INFO
   ```

2. Levantar servicios (local):

   ```bash
   docker compose -f docker-compose.prod.yml up -d --build
   ```

3. Ejecutar migraciones (si tu plataforma no ejecuta `start_with_migrations.sh` automáticamente):

   - Usando el contenedor `backend`:

     ```bash
     docker compose -f docker-compose.prod.yml run --rm backend alembic upgrade head
     ```

   - O, si tu proveedor ofrece jobs, crea un job que ejecute el mismo comando en la imagen del backend.

4. Ejecutar seed (si necesitas poblar datos iniciales):

   ```bash
   docker compose -f docker-compose.prod.yml run --rm backend python -m app.seed
   ```

5. Backups y restore

   - Crear backup:

     ```bash
     DATABASE_URL="${DATABASE_URL}" BACKUP_DIR=./backups ./scripts/backup_db.sh
     ```

   - Restaurar:

     ```bash
     ./scripts/restore_db.sh ./backups/db-backup-YYYYMMDDT....dump "postgresql://user:pass@host:5432/targetdb"
     ```

Consejos para plataformas gestionadas (Render / Heroku / Cloud Run)
-----------------------------------------------------------------
- Configura `DATABASE_URL` y `SECRET_KEY` como secretos/env vars desde la consola de tu proveedor.
- Añade un job/command que ejecute migraciones antes de rotar la nueva versión. Por ejemplo, en Render crea un `run-migrations` job que ejecute: `alembic upgrade head`.
- Alternativamente, usa `scripts/start_with_migrations.sh` como entrypoint de contenedor: esta opción intenta ejecutar migraciones en el arranque del contenedor y luego arranca la app. Es idempotente pero ten cuidado con despliegues multi-replicas simultáneos — preferible coordinar migraciones desde un job/step de CI.

Ejemplo de comando para CI (GitHub Actions) que aplica migraciones antes de desplegar:

```yaml
- name: Run DB migrations
  run: |
    docker run --rm -e DATABASE_URL="$DATABASE_URL" your-backend-image:latest alembic upgrade head
```

Notas de seguridad
------------------
- Nunca expongas `SECRET_KEY` ni `DATABASE_URL` en repositorios públicos.
- Asegura backups cifrados y rotación de claves según política de seguridad.
