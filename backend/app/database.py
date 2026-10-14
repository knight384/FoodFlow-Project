"""
PostgreSQL connectivity infrastructure.

Phase 1 scope only: establishes a SQLAlchemy engine/session factory and a
lightweight connectivity check used by the /health/db endpoint.

Explicitly NOT included in this phase (per the controlled implementation
process for Phase 1):
- No ORM models for business tables (users, locations, meal_types,
  historical_consumption, forecasted_demand, planned_quantity,
  redistribution_recommendation, import_job, import_record_error).
- No Alembic/migration setup.
- No seed data.

The full logical schema is defined in Database Specification v1.0 and will
be implemented as ORM models + migrations in a later implementation phase.
"""

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

settings = get_settings()

# `pool_pre_ping=True` avoids using stale/dropped connections — a reasonable,
# low-risk default for local development; not a production tuning decision.
engine = create_engine(settings.database_url, pool_pre_ping=True, future=True)


class Base(DeclarativeBase):
    """
    Shared SQLAlchemy declarative base for all ORM models (Phase 2:
    Database Implementation). Each business module (app/modules/<name>/models.py)
    defines its own model(s) against this same Base/metadata, consistent
    with the modular-monolith design (TRD v1.0 Section 5/8) while still
    persisting to a single PostgreSQL database (Database Specification
    v1.0 Section 3).
    """

SessionLocal = sessionmaker(
    bind=engine, autoflush=False, autocommit=False, future=True
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a database session and ensures it is
    closed after the request completes. No business queries are issued
    against it in Phase 1 — this exists purely as connectivity infrastructure
    for later phases to build on.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """Context-manager form of get_db(), for non-request-scoped use (e.g., scripts)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_connection() -> tuple[bool, str | None]:
    """
    Attempt a minimal round-trip query (`SELECT 1`) against PostgreSQL.

    Returns (is_connected, error_message). Used only by the health-check
    endpoint (Section: Health Checks) — this is infrastructure verification,
    not a business capability.
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True, None
    except Exception as exc:  # noqa: BLE001 - health check intentionally broad
        return False, str(exc)
