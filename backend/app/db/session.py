"""
Async database session factory.

Uses SQLAlchemy 2.0 async engine with aiosqlite for SQLite.
"""
from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings
from app.utils import normalize_vi

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,          # log SQL when DEBUG=true
    connect_args={"check_same_thread": False},
    future=True,
)


@event.listens_for(engine.sync_engine, "connect")
def _register_sqlite_functions(dbapi_conn, _connection_record) -> None:
    """Register custom functions available to every SQLite connection."""
    dbapi_conn.create_function("normalize_vi", 1, normalize_vi)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,   # keep ORM objects usable after commit
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session for the lifetime of a single request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
