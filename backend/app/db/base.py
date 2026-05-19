"""
SQLAlchemy declarative base.

All ORM models import Base from here so Alembic can discover them
automatically via metadata.
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""
    pass
