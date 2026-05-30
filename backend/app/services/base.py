"""Base service class with common patterns."""
from __future__ import annotations

from typing import TypeVar

from fastapi import HTTPException, status

T = TypeVar("T")


class BaseService:
    """Base service with common utility methods."""

    @staticmethod
    async def get_or_404(obj: T | None, model_name: str) -> T:
        """Raise 404 HTTPException if object is None."""
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{model_name} not found",
            )
        return obj

    @staticmethod
    def calculate_offset(page: int, page_size: int) -> int:
        """Convert 1-based page number to 0-based offset."""
        return (page - 1) * page_size
