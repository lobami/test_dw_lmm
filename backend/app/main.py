import os
import logging
from logging import StreamHandler
from fastapi import FastAPI, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from .database import engine

# Import package modules so SQLAlchemy models are registered
from .users import models as users_models
from .campaigns import models as campaigns_models
from .users import routers as users_router
from .campaigns import routers as campaigns_router

from .database import Base

# Create tables if they do not exist (development). In production rely on Alembic migrations.
Base.metadata.create_all(bind=engine)

# Structured JSON logging configuration. Honor LOG_LEVEL env var.
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logger = logging.getLogger("app")
logger.setLevel(log_level)
handler = StreamHandler()
try:
    from pythonjsonlogger import jsonlogger

    fmt = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s %(module)s')
    handler.setFormatter(fmt)
except Exception:
    # Fallback to plain text formatter if python-json-logger is not installed
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s'))

logger.addHandler(handler)
logger.propagate = False
logger.info("Starting Campaign Analytics API", extra={"allowed_origins": os.getenv('FRONTEND_ORIGINS', '')})

# NOTE: Runtime ALTER TABLE helpers were removed. Use Alembic migrations instead.

app = FastAPI(title="Campaign Analytics API")


@app.middleware("http")
async def enforce_https(request: Request, call_next):
    """Reject non-HTTPS requests when running in production.

    Many PaaS providers terminate TLS at the platform and forward the original
    scheme in the `X-Forwarded-Proto` header — we respect that header. This
    middleware only runs when `ENV=production` to avoid breaking local
    development (where HTTP is normal).
    """
    if os.getenv("ENV", "").lower() == "production":
        proto = request.headers.get("x-forwarded-proto", request.url.scheme)
        if proto != "https":
            # 426 Upgrade Required: client should use HTTPS
            return Response(status_code=426, content='{"detail":"HTTPS required"}', media_type="application/json")
    return await call_next(request)

@app.get("/")
def read_root():
    return {"message": "Welcome to Campaign Analytics API"}

@app.get("/health")
def health_check():
    """Health check that verifies DB connectivity.

    Returns 200 when a simple SELECT 1 succeeds, otherwise 503.
    """
    try:
        from .database import SessionLocal
        db = SessionLocal()
        # Run a lightweight query
        db.execute("SELECT 1")
        db.close()
        return {"status": "ok"}
    except Exception as e:
        logger.exception("healthcheck_db_failed", extra={"error": str(e)})
        from fastapi import Response
        return Response(status_code=503, content='{"status": "unhealthy"}')


@app.get("/metrics")
def metrics() -> Response:
    """Expose Prometheus metrics if prometheus_client is installed.

    If prometheus_client is not available the endpoint returns 501.
    """
    try:
        from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    except Exception:
        return Response(status_code=501, content="metrics not enabled")

    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


# CORS middleware configuration
FRONTEND_ORIGINS = os.getenv(
    "FRONTEND_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
)

# Allow multiple origins (comma-separated). Trim whitespace and ignore empties.
allowed_origins = [o.strip() for o in FRONTEND_ORIGINS.split(",") if o.strip()]

# In production, require explicit FRONTEND_ORIGINS (no '*') to avoid cookie issues.
if os.getenv("ENV", "").lower() == "production":
    if not allowed_origins or any(o == "*" for o in allowed_origins):
        raise RuntimeError(
            "In production set FRONTEND_ORIGINS to a comma-separated list of allowed origins (do not use '*')."
        )

# Configure CORS to allow credentials and only the specific frontend origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(campaigns_router.router)
app.include_router(users_router.router)
