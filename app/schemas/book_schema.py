"""Pydantic schemas for Book request/response."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class BookCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=256)
    author: str = Field(min_length=1, max_length=128)
    isbn: Optional[str] = Field(default=None, max_length=20)
    category: Optional[str] = Field(default=None, max_length=64)
    description: Optional[str] = None
    total_quantity: int = Field(default=1, ge=1)


class BookUpdateRequest(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=256)
    author: Optional[str] = Field(default=None, min_length=1, max_length=128)
    isbn: Optional[str] = Field(default=None, max_length=20)
    category: Optional[str] = Field(default=None, max_length=64)
    description: Optional[str] = None
    total_quantity: Optional[int] = Field(default=None, ge=1)


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    isbn: Optional[str]
    category: Optional[str]
    description: Optional[str]
    total_quantity: int
    available_quantity: int
    is_available: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
