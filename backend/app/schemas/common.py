"""Common Pydantic schemas: pagination, generic responses."""
from __future__ import annotations

from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class PaginationMeta(BaseModel):
    """Pagination metadata returned with list endpoints."""

    total: int = Field(..., description="Total number of records")
    page: int = Field(..., description="Current page (1-based)")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper.

    Example:
        PaginatedResponse[BookRead]
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    items: List[T]
    meta: PaginationMeta


class MessageResponse(BaseModel):
    """Generic success/info message response."""

    message: str


class ErrorDetail(BaseModel):
    """A single field-level validation error."""

    field: str
    message: str


class ErrorResponse(BaseModel):
    """Standard error response body."""

    detail: str
    errors: Optional[List[ErrorDetail]] = None
