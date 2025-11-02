import os
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()


def get_database_url() -> str:
    """Return the database URL from the environment or a sensible SQLite fallback.

    Uses the DATABASE_URL env var when present (e.g. postgresql://...)
    otherwise falls back to the project's local sqlite file.
    """
    return os.getenv("DATABASE_URL") or "sqlite:///./campaigns.db"
