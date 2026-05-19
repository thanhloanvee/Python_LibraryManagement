"""
Reviews router.

RBAC:
  GET  /reviews             → Public (active reviews only)
  POST /reviews             → Reader (must have borrowed the book)
  PATCH /reviews/{id}       → Owner only
  PATCH /reviews/{id}/status → Admin only
  DELETE /reviews/{id}      → Owner or Admin
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import get_current_active_user
from app.dependencies.rbac import require_admin, require_reader
from app.models.review import ReviewStatus
from app.models.user import User, UserRole
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.review import (
    ReviewAdminUpdate,
    ReviewCreate,
    ReviewRead,
    ReviewUpdate,
)
from app.services.review import ReviewService
from app.utils.pagination import Paginator, make_paginated_response

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.get(
    "",
    response_model=PaginatedResponse[ReviewRead],
    summary="List reviews",
)
async def list_reviews(
    book_id: Optional[int] = Query(default=None),
    user_id: Optional[int] = Query(default=None),
    pagination: Paginator = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """Public listing — only ACTIVE reviews are returned."""
    service = ReviewService(db)
    items, total = await service.list_reviews(
        book_id=book_id,
        user_id=user_id,
        status=ReviewStatus.ACTIVE,
        page=pagination.page,
        page_size=pagination.page_size,
    )
    return make_paginated_response(
        [ReviewRead.model_validate(r) for r in items],
        total,
        pagination.page,
        pagination.page_size,
    )


@router.post(
    "",
    response_model=ReviewRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a review (must have borrowed the book)",
)
async def create_review(
    data: ReviewCreate,
    current_user: User = Depends(require_reader),
    db: AsyncSession = Depends(get_db),
):
    """
    Reader creates a review. Enforces:
    - Must have borrowed the book
    - One review per user per book
    """
    service = ReviewService(db)
    return await service.create_review(data, current_user.id)


@router.patch(
    "/{review_id}",
    response_model=ReviewRead,
    summary="Update own review",
)
async def update_review(
    review_id: int,
    data: ReviewUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    service = ReviewService(db)
    return await service.update_review(review_id, data, current_user.id)


@router.patch(
    "/{review_id}/status",
    response_model=ReviewRead,
    dependencies=[Depends(require_admin)],
    summary="Toggle review visibility (Admin)",
)
async def admin_update_review_status(
    review_id: int,
    data: ReviewAdminUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = ReviewService(db)
    return await service.admin_update_review(review_id, data)


@router.delete(
    "/{review_id}",
    response_model=MessageResponse,
    summary="Delete a review",
)
async def delete_review(
    review_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    service = ReviewService(db)
    is_admin = current_user.role == UserRole.ADMIN
    await service.delete_review(review_id, current_user.id, is_admin=is_admin)
    return MessageResponse(message="Review deleted successfully.")
