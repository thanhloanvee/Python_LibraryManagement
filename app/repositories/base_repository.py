"""
BaseRepository — generic CRUD operations.
Receives an injected SQLAlchemy Session; no Flask context required.
"""

from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import Base

T = TypeVar("T", bound=Base)  # type: ignore[type-arg]


class BaseRepository(Generic[T]):
    """Standard CRUD methods wrapping a SQLAlchemy session."""

    def __init__(self, model: Type[T], db: Session) -> None:
        self.model = model
        self.db = db

    # ── Read ──────────────────────────────────────────────────────

    def get_by_id(self, record_id: int) -> Optional[T]:
        return self.db.get(self.model, record_id)

    def get_all(self) -> List[T]:
        return self.db.execute(select(self.model)).scalars().all()

    # ── Write ─────────────────────────────────────────────────────

    def add(self, instance: T) -> T:
        self.db.add(instance)
        self.db.flush()  # assign PK without committing
        return instance

    def delete(self, instance: T) -> None:
        self.db.delete(instance)
        self.db.flush()

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()
