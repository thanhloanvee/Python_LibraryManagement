"""Pydantic schemas for BorrowRecord and Fine request/response."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class BorrowCreateRequest(BaseModel):
    book_id: int = Field(ge=1)


class FineResponse(BaseModel):
    id: int
    borrow_id: int
    overdue_days: int
    amount: float
    is_paid: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BorrowResponse(BaseModel):
    id: int
    user_id: int
    book_id: int
    book_title: Optional[str]
    borrow_date: datetime
    due_date: datetime
    return_date: Optional[datetime]
    status: str
    fine: Optional[FineResponse]

    model_config = ConfigDict(from_attributes=True)
