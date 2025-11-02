import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Ensure the backend package is importable (add repo root / backend to path)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

# Import your model's MetaData object here
from app.database import Base

target_metadata = Base.metadata

# Prefer DATABASE_URL env var if present
db_url = os.getenv("DATABASE_URL")
if not db_url:
    # try to import app config helper
    try:
        from app.config import get_database_url

        db_url = get_database_url()
    except Exception:
        db_url = config.get_main_option("sqlalchemy.url")

if db_url:
    config.set_main_option("sqlalchemy.url", db_url)


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
