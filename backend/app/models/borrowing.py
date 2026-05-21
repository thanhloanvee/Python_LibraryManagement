"""Borrowing ORM model."""
from __future__ import annotations

import enum
from datetime import date, datetime, timezone

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class BorrowingStatus(str, enum.Enum):
    BORROWED = "borrowed"
    RETURNED = "returned"
    OVERDUE = "overdue"


class BookCondition(str, enum.Enum):
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    DAMAGED = "damaged"


class Borrowing(Base):
    """Represents the ``borrowings`` table."""

    __tablename__ = "borrowings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    book_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("books.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    borrow_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    return_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    status: Mapped[BorrowingStatus] = mapped_column(
        Enum(BorrowingStatus), default=BorrowingStatus.BORROWED, nullable=False, index=True
    )
    book_condition: Mapped[BookCondition | None] = mapped_column(
        Enum(BookCondition), nullable=True
    )

    renewed_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    fine_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    fine_paid: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    librarian_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

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

    user: Mapped["User"] = relationship(  # noqa: F821
        "User", back_populates="borrowings", lazy="select"
    )
    book: Mapped["Book"] = relationship(  # noqa: F821
        "Book", back_populates="borrowings", lazy="select"
    )

    @property
    def is_overdue(self) -> bool:
        """True when not returned and past due_date."""
        if self.status == BorrowingStatus.RETURNED:
            return False
        return self.due_date < date.today()

    @property
    def days_overdue(self) -> int:
        """Number of days past due_date."""
        if not self.is_overdue:
            return 0
        return (date.today() - self.due_date).days

    @property
    def days_until_due(self) -> int:
        """Days remaining until due; negative means overdue."""
        if self.status == BorrowingStatus.RETURNED:
            return 0
        delta = self.due_date - date.today()
        return delta.days

    def calculate_fine(self, fine_per_day: float) -> float:
        """Calculate fine based on days overdue."""
        return self.days_overdue * fine_per_day

    def __repr__(self) -> str:
        return (
            f"<Borrowing id={self.id} user_id={self.user_id} "
            f"book_id={self.book_id} status={self.status}>"
        )
