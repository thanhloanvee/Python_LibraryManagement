"""
User model.

Roles:
  admin      – full system access
  librarian  – manage books, view reports, process borrows
  member     – borrow / return books
"""

import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from app.database import Base


class RoleEnum(str, enum.Enum):
    ADMIN = "admin"
    LIBRARIAN = "librarian"
    MEMBER = "member"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    email = Column(String(128), unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=False)
    role = Column(
        Enum(RoleEnum),
        nullable=False,
        default=RoleEnum.MEMBER,
    )
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    borrow_records = relationship(
        "BorrowRecord", back_populates="user", lazy="dynamic"
    )

    # ── Helpers ──────────────────────────────────────────────────

    def is_admin(self) -> bool:
        return self.role == RoleEnum.ADMIN

    def is_librarian(self) -> bool:
        return self.role == RoleEnum.LIBRARIAN

    def is_member(self) -> bool:
        return self.role == RoleEnum.MEMBER

    def active_borrow_count(self, db_session) -> int:
        """Number of books currently borrowed — pass the active Session."""
        from sqlalchemy import select, func
        from app.models.borrow import BorrowRecord, BorrowStatusEnum
        return db_session.execute(
            select(func.count()).select_from(BorrowRecord).where(
                BorrowRecord.user_id == self.id,
                BorrowRecord.status == BorrowStatusEnum.BORROWED,
            )
        ).scalar_one()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role.value,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self) -> str:
        return f"<User {self.username} ({self.role.value})>"
