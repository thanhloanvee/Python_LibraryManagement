"""
Pagination utility — converts page/page_size query params into offset/limit
and wraps list results in PaginatedResponse.
"""
from __future__ import annotations

import math
from typing import Generic, List, Tuple, TypeVar

from fastapi import Query

from app.schemas.common import PaginatedResponse, PaginationMeta

T = TypeVar("T")


class Paginator:
    """FastAPI dependency that parses page/page_size query params."""

    def __init__(
        self,
        page: int = Query(default=1, ge=1, description="Page number (1-based)"),
        page_size: int = Query(
            default=20, ge=1, le=100, description="Items per page"
        ),
    ) -> None:
        self.page = page
        self.page_size = page_size

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


def make_paginated_response(
    items: List[T],
    total: int,
    page: int,
    page_size: int,
) -> PaginatedResponse[T]:
    total_pages = max(1, math.ceil(total / page_size))
    return PaginatedResponse(
        items=items,
        meta=PaginationMeta(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        ),
    )
