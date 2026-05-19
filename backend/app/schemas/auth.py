"""Authentication Pydantic schemas."""
from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """POST /auth/login body."""

    username: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=6)


class RegisterRequest(BaseModel):
    """POST /auth/register body."""

    username: str = Field(
        ...,
        min_length=3,
        max_length=255,
        pattern=r"^[a-zA-Z0-9_]+$",
        description="Only letters, digits, and underscores",
    )
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    address: str | None = Field(default=None, max_length=500)


class TokenResponse(BaseModel):
    """Successful login response containing JWT tokens."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """POST /auth/refresh body."""

    refresh_token: str


class ChangePasswordRequest(BaseModel):
    """POST /auth/change-password body."""

    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=128)
