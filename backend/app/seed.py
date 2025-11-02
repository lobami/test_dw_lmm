"""Module wrapper to run the repository seed from the `app` package.

Allows running:

    python -m app.seed

or (from backend/):

    python seed.py

This file delegates to the top-level `seed.py` script which lives in the backend/ folder.
"""
import logging

logger = logging.getLogger("app.seed")

try:
    # Import the top-level seed module (backend/seed.py) when running from backend/ directory
    import seed as seed_module
except Exception as e:
    logger.exception("failed_to_import_top_level_seed", extra={"error": str(e)})
    raise


def load_data():
    seed_module.load_data()


def ensure_default_admin():
    seed_module.ensure_default_admin()


if __name__ == "__main__":
    # Run full seed (idempotent)
    load_data()
    ensure_default_admin()
