"""Review ORM model."""
from __future__ import annotations

import enum
from datetime import datetime

from app.db.base import ICT

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    SmallInteger,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ReviewStatus(int, enum.Enum):
    HIDDEN = 0
    ACTIVE = 1


class Review(Base):
    """Represents the ``reviews`` table."""

    __tablename__ = "reviews"
    __table_args__ = (
        UniqueConstraint("user_id", "book_id", name="uq_review_user_book"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    book_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    rating: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[ReviewStatus] = mapped_column(
        Enum(ReviewStatus), default=ReviewStatus.ACTIVE, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(ICT),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(ICT),
        onupdate=lambda: datetime.now(ICT),
        server_default=func.now(),
        nullable=False,
    )

    book: Mapped["Book"] = relationship(  # noqa: F821
        "Book", back_populates="reviews", lazy="select"
    )
    user: Mapped["User"] = relationship(  # noqa: F821
        "User", back_populates="reviews", lazy="select"
    )

    def __repr__(self) -> str:
        return (
            f"<Review id={self.id} user_id={self.user_id} "
            f"book_id={self.book_id} rating={self.rating}>"
        )
