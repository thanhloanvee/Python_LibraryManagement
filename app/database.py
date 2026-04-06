"""
app/database.py — SQLAlchemy engine, session factory, and Base.

All models import `Base` from here.
All routes/services get a `Session` via the `get_db` dependency.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session

from app.config import get_settings


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""
    pass


def _build_engine():
    settings = get_settings()
    connect_args = (
        {"check_same_thread": False}
        if settings.DATABASE_URL.startswith("sqlite")
        else {}
    )
    return create_engine(settings.DATABASE_URL, connect_args=connect_args)


engine = _build_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ── FastAPI dependency ─────────────────────────────────────────

def get_db():
    """Yield a database session and close it when done."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Table creation helper ──────────────────────────────────────

def create_tables() -> None:
    """Create all tables (called at app startup)."""
    from app.models import user, book, borrow  # noqa: F401 — register models
    Base.metadata.create_all(bind=engine)
