"""
SQLAlchemy declarative base.

All ORM models import Base from here so Alembic can discover them
automatically via metadata.
"""
from zoneinfo import ZoneInfo

from sqlalchemy.orm import DeclarativeBase

ICT = ZoneInfo("Asia/Ho_Chi_Minh")


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""
    pass
