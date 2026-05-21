"""
Users router.

RBAC:
  - GET /users         → Admin only
  - GET /users/me      → Any authenticated user (in auth router)
  - GET /users/{id}    → Admin only
  - POST /users        → Admin only
  - PATCH /users/me    → Any authenticated user
  - PATCH /users/{id}  → Admin only
  - DELETE /users/{id} → Admin only
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import get_current_active_user
from app.dependencies.rbac import require_admin
from app.models.user import User, UserRole, UserStatus
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.user import UserAdminUpdate, UserCreate, UserRead, UserUpdate
from app.services.user import UserService
from app.utils.pagination import Paginator, make_paginated_response

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "",
    response_model=PaginatedResponse[UserRead],
    dependencies=[Depends(require_admin)],
    summary="List all users (Admin)",
)
async def list_users(
    role: Optional[UserRole] = Query(default=None),
    status: Optional[UserStatus] = Query(default=None),
    search: Optional[str] = Query(default=None),
    pagination: Paginator = Depends(),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    items, total = await service.list_users(
        role=role,
        status=status,
        search=search,
        page=pagination.page,
        page_size=pagination.page_size,
    )
    return make_paginated_response(
        [UserRead.model_validate(u) for u in items],
        total,
        pagination.page,
        pagination.page_size,
    )


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
    summary="Create a user (Admin)",
)
async def create_user(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    return await service.create_user(data)


@router.get(
    "/me",
    response_model=UserRead,
    summary="Get own profile",
)
async def get_own_profile(
    current_user: User = Depends(get_current_active_user),
):
    return current_user


@router.patch(
    "/me",
    response_model=UserRead,
    summary="Update own profile",
)
async def update_own_profile(
    data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    return await service.update_profile(current_user, data)


@router.get(
    "/{user_id}",
    response_model=UserRead,
    dependencies=[Depends(require_admin)],
    summary="Get a user by ID (Admin)",
)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    return await service.get_or_404(user_id)


@router.patch(
    "/{user_id}",
    response_model=UserRead,
    dependencies=[Depends(require_admin)],
    summary="Update a user (Admin)",
)
async def admin_update_user(
    user_id: int,
    data: UserAdminUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    return await service.admin_update_user(user_id, data)


@router.delete(
    "/{user_id}",
    response_model=MessageResponse,
    dependencies=[Depends(require_admin)],
    summary="Delete a user (Admin)",
)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    await service.delete_user(user_id)
    return MessageResponse(message="User deleted successfully.")
