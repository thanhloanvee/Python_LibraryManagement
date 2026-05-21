"""Review Pydantic schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.review import ReviewStatus
from app.schemas.user import UserPublic


class ReviewRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    book_id: int
    user_id: int
    user: UserPublic | None = None
    rating: int
    comment: str | None
    status: ReviewStatus
    created_at: datetime
    updated_at: datetime


class ReviewCreate(BaseModel):
    book_id: int
    rating: int = Field(..., ge=1, le=5, description="Rating 1–5 stars")
    comment: Optional[str] = Field(default=None, max_length=2000)


class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    comment: Optional[str] = Field(default=None, max_length=2000)


class ReviewAdminUpdate(BaseModel):
    """Admin can hide/show a review."""

    status: ReviewStatus
