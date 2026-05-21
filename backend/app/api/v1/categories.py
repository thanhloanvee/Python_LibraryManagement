"""
Categories router.

RBAC:
  - GET  /categories       → Public (no auth required)
  - GET  /categories/{id}  → Public
  - POST /categories       → Librarian or Admin
  - PATCH /categories/{id} → Librarian or Admin
  - DELETE /categories/{id}→ Admin only
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.rbac import require_admin, require_librarian
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.schemas.common import MessageResponse, PaginatedResponse
from app.services.category import CategoryService
from app.utils.pagination import Paginator, make_paginated_response

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get(
    "",
    response_model=PaginatedResponse[CategoryRead],
    summary="List all categories",
)
async def list_categories(
    search: Optional[str] = Query(default=None),
    pagination: Paginator = Depends(),
    db: AsyncSession = Depends(get_db),
):
    service = CategoryService(db)
    items, total = await service.list_categories(
        search=search,
        page=pagination.page,
        page_size=pagination.page_size,
    )
    return make_paginated_response(
        [CategoryRead.model_validate(c) for c in items],
        total,
        pagination.page,
        pagination.page_size,
    )


@router.get(
    "/{category_id}",
    response_model=CategoryRead,
    summary="Get a category by ID",
)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = CategoryService(db)
    return await service.get_or_404(category_id)


@router.post(
    "",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_librarian)],
    summary="Create a category (Librarian/Admin)",
)
async def create_category(
    data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
):
    service = CategoryService(db)
    return await service.create_category(data)


@router.patch(
    "/{category_id}",
    response_model=CategoryRead,
    dependencies=[Depends(require_librarian)],
    summary="Update a category (Librarian/Admin)",
)
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = CategoryService(db)
    return await service.update_category(category_id, data)


@router.delete(
    "/{category_id}",
    response_model=MessageResponse,
    dependencies=[Depends(require_admin)],
    summary="Delete a category (Admin)",
)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = CategoryService(db)
    await service.delete_category(category_id)
    return MessageResponse(message="Category deleted successfully.")
