"""User Pydantic schemas."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole, UserStatus


class UserRead(BaseModel):
    """Full user representation returned from GET endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    full_name: str
    phone: str | None
    address: str | None
    role: UserRole
    status: UserStatus
    created_at: datetime
    updated_at: datetime


class UserPublic(BaseModel):
    """Minimal public user info embedded in other responses (e.g. borrowings)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    full_name: str
    role: UserRole


class UserCreate(BaseModel):
    """Admin-only: create a user with an explicit role.
    Regular registration uses auth.RegisterRequest instead.
    """

    username: str = Field(
        ...,
        min_length=3,
        max_length=255,
        pattern=r"^[a-zA-Z0-9_]+$",
    )
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    address: str | None = Field(default=None, max_length=500)
    role: UserRole = UserRole.READER
    status: UserStatus = UserStatus.ACTIVE


class UserUpdate(BaseModel):
    """PATCH /users/{id} — partial update of mutable profile fields."""

    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    address: str | None = Field(default=None, max_length=500)
    email: EmailStr | None = None


class UserAdminUpdate(BaseModel):
    """Admin-only PATCH: can also change role and status."""

    full_name: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    address: str | None = Field(default=None, max_length=500)
    email: EmailStr | None = None
    role: UserRole | None = None
    status: UserStatus | None = None
