"""Book ORM model."""
from __future__ import annotations

import enum
from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class BookStatus(str, enum.Enum):
    AVAILABLE = "Có sẵn"
    DAMAGED = "Hư hỏng"
    LOST = "Mất"


class BookLanguage(str, enum.Enum):
    VIETNAMESE = "vi"
    ENGLISH = "en"


class Book(Base):
    """Represents the ``books`` table."""

    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    author: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    isbn: Mapped[str | None] = mapped_column(
        String(20), unique=True, nullable=True, index=True
    )
    publisher: Mapped[str | None] = mapped_column(String(255), nullable=True)
    publication_year: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    language: Mapped[BookLanguage] = mapped_column(
        Enum(BookLanguage), default=BookLanguage.VIETNAMESE, nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    cover_image: Mapped[str | None] = mapped_column(String(255), nullable=True)

    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    available_quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[BookStatus] = mapped_column(
        Enum(BookStatus), default=BookStatus.AVAILABLE, nullable=False
    )

    category_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )

    category: Mapped["Category | None"] = relationship(  # noqa: F821
        "Category", back_populates="books", lazy="select"
    )
    borrowings: Mapped[list["Borrowing"]] = relationship(  # noqa: F821
        "Borrowing", back_populates="book", lazy="select"
    )
    reviews: Mapped[list["Review"]] = relationship(  # noqa: F821
        "Review", back_populates="book", lazy="select"
    )

    @property
    def is_available(self) -> bool:
        """True when the book can be lent."""
        return (
            self.status == BookStatus.AVAILABLE and self.available_quantity > 0
        )

    def __repr__(self) -> str:
        return f"<Book id={self.id} title={self.title!r}>"
