"""Book Pydantic schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.book import BookLanguage, BookStatus
from app.schemas.category import CategoryRead


class BookRead(BaseModel):
    """Full book representation returned from GET endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    author: str
    isbn: str | None
    publisher: str | None
    publication_year: int | None
    language: BookLanguage
    description: str | None
    cover_image: str | None
    quantity: int
    available_quantity: int
    status: BookStatus
    category_id: int | None
    category: CategoryRead | None
    created_at: datetime
    updated_at: datetime


class BookSummary(BaseModel):
    """Minimal book info embedded in borrowings/reviews."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    author: str
    cover_image: str | None
    status: BookStatus
    available_quantity: int


class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    isbn: Optional[str] = Field(default=None, max_length=20)
    publisher: Optional[str] = Field(default=None, max_length=255)
    publication_year: Optional[int] = Field(default=None, ge=-4000, le=2100)
    language: BookLanguage = BookLanguage.VIETNAMESE
    description: Optional[str] = None
    cover_image: Optional[str] = Field(default=None, max_length=255)
    quantity: int = Field(default=1, ge=0)
    available_quantity: int = Field(default=1, ge=0)
    status: BookStatus = BookStatus.AVAILABLE
    category_id: Optional[int] = None

    @model_validator(mode="after")
    def available_cannot_exceed_total(self) -> "BookCreate":
        if self.available_quantity > self.quantity:
            raise ValueError(
                "available_quantity cannot exceed total quantity"
            )
        return self


class BookUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    author: Optional[str] = Field(default=None, min_length=1, max_length=255)
    isbn: Optional[str] = Field(default=None, max_length=20)
    publisher: Optional[str] = Field(default=None, max_length=255)
    publication_year: Optional[int] = Field(default=None, ge=-4000, le=2100)
    language: Optional[BookLanguage] = None
    description: Optional[str] = None
    cover_image: Optional[str] = Field(default=None, max_length=255)
    quantity: Optional[int] = Field(default=None, ge=0)
    available_quantity: Optional[int] = Field(default=None, ge=0)
    status: Optional[BookStatus] = None
    category_id: Optional[int] = None

    @model_validator(mode="after")
    def available_cannot_exceed_total(self) -> "BookUpdate":
        if (
            self.available_quantity is not None
            and self.quantity is not None
            and self.available_quantity > self.quantity
        ):
            raise ValueError(
                "available_quantity cannot exceed total quantity"
            )
        return self


class BookFilter(BaseModel):
    """Query-parameter filter DTO for book listing."""

    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    category_id: Optional[int] = None
    status: Optional[BookStatus] = None
    language: Optional[BookLanguage] = None
    search: Optional[str] = None   # full-text across title + author
