import os
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import get_database_url

SQLALCHEMY_DATABASE_URL = get_database_url()

# SQLite needs a special connect arg to allow multithreaded access from the app
# When running tests we prefer an in-memory DB shared across threads (StaticPool)
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    if os.getenv("TESTING") == "1" or SQLALCHEMY_DATABASE_URL == "sqlite:///:memory:":
        engine = create_engine(
            SQLALCHEMY_DATABASE_URL,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency to get DB session for FastAPI endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
