"""Borrowing Pydantic schemas."""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.borrowing import BookCondition, BorrowingStatus
from app.schemas.book import BookSummary
from app.schemas.user import UserPublic


class BorrowingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    book_id: int
    user: UserPublic | None = None
    book: BookSummary | None = None
    borrow_date: date
    due_date: date
    return_date: date | None
    status: BorrowingStatus
    book_condition: BookCondition | None
    renewed_count: int
    fine_amount: float
    fine_paid: bool
    librarian_notes: str | None
    # Computed helpers
    is_overdue: bool
    days_overdue: int
    days_until_due: int
    created_at: datetime
    updated_at: datetime


class BorrowingCreate(BaseModel):
    """Librarian issues a book to a reader."""

    user_id: int
    book_id: int
    due_date: Optional[date] = Field(
        default=None,
        description=(
            "Override due date; defaults to today + BORROWING_PERIOD_DAYS"
        ),
    )

    @model_validator(mode="after")
    def due_date_in_future(self) -> "BorrowingCreate":
        if self.due_date is not None and self.due_date <= date.today():
            raise ValueError("due_date must be in the future")
        return self


class ReturnBookRequest(BaseModel):
    """Librarian processes a book return with optional notes."""

    book_condition: Optional[BookCondition] = None
    librarian_notes: Optional[str] = Field(default=None, max_length=2000)


class RenewBorrowingRequest(BaseModel):
    """Reader requests a renewal; librarian may approve."""

    extend_days: int = Field(
        default=14,
        ge=1,
        le=30,
        description="Number of days to extend the due date",
    )


class MarkFinePaidRequest(BaseModel):
    """Librarian marks the fine as collected."""

    fine_paid: bool = True


class BorrowingFilter(BaseModel):
    status: Optional[BorrowingStatus] = None
    user_id: Optional[int] = None
    book_id: Optional[int] = None
    overdue_only: bool = False
