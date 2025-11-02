# Migraciones (Alembic)

Este proyecto usa Alembic para versionar el esquema de la base de datos.

Archivos añadidos:
- `alembic.ini` — configuración mínima para Alembic ubicada en `backend/`.
- `migrations/` — carpeta con `env.py` y `versions/0001_initial.py`.

Pasos rápidos (desarrollo)

1. Activar entorno virtual y instalar dependencias:

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
```

2. Inicializar (si no existe) y aplicar migraciones:

```bash
# desde backend/
# crea la carpeta migrations si es necesario: ya está en el repo
alembic upgrade head
```

3. Qué hace la migración inicial

- Crea las tablas definidas por `app` (metadata de `app.database.Base`).

Nota importante sobre seed / cargas de datos

- Las cargas de datos (seed) están separadas de las migraciones de esquema. No se ejecutan automáticamente durante `alembic upgrade head`.
- Para cargar los CSVs y crear el admin por defecto ejecute explícitamente el script de seed:

```bash
# desde el directorio backend/
python seed.py
# o como módulo del paquete app:
python -m app.seed
```

Esto mantiene las migraciones (esquema) separadas de las cargas masivas de datos, lo que es una práctica recomendada para entornos de producción.

Notas y precauciones

- La migración inicial contiene pasos de carga de datos (CSV) — esto es conveniente para desarrollo. En producción recomendamos separar las migraciones de esquema de las cargas masivas de datos y ejecutar las cargas en jobs controlados.
- Antes de correr migraciones en producción, pruebe en un entorno similar (same DB engine) y haga backup.
- Después de aplicar correctamente las migraciones, puede eliminar la lógica temporal de `ALTER TABLE` en `app/main.py`.
