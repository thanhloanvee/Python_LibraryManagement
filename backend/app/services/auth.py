"""Authentication service."""
from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_refresh_token,
)
from app.models.user import User, UserRole, UserStatus
from app.repositories.user import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse

settings = get_settings()


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self._repo = UserRepository(db)

    async def login(self, data: LoginRequest) -> TokenResponse:
        """Authenticate user by username + password and return JWT tokens."""
        user = await self._repo.get_by_username(data.username)
        if not user or not verify_password(data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if user.status != UserStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account is inactive. Please contact the librarian.",
            )
        return self._build_tokens(user)

    async def register(self, data: RegisterRequest) -> User:
        """Register a new reader account."""
        # Check username uniqueness
        if await self._repo.get_by_username(data.username):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="This username has already been taken.",
            )
        # Check email uniqueness
        if await self._repo.get_by_email(data.email):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="This email address has already been taken.",
            )

        user = User(
            username=data.username,
            email=data.email,
            password_hash=hash_password(data.password),
            full_name=data.full_name,
            phone=data.phone,
            address=data.address,
            role=UserRole.READER,
            status=UserStatus.ACTIVE,
        )
        return await self._repo.create(user)

    async def refresh(self, refresh_token: str) -> TokenResponse:
        """Issue a new access token from a valid refresh token."""
        from jwt.exceptions import InvalidTokenError

        try:
            payload = verify_refresh_token(refresh_token)
            user_id = int(payload["sub"])
        except (InvalidTokenError, KeyError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        user = await self._repo.get_by_id(user_id)
        if not user or user.status != UserStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )
        return self._build_tokens(user)

    async def change_password(
        self, user: User, current_password: str, new_password: str
    ) -> None:
        """Change password after verifying the current one."""
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )
        user.password_hash = hash_password(new_password)
        await self._repo.save(user)

    @staticmethod
    def _build_tokens(user: User) -> TokenResponse:
        extra = {"role": user.role.value, "username": user.username}
        return TokenResponse(
            access_token=create_access_token(user.id, extra_claims=extra),
            refresh_token=create_refresh_token(user.id),
        )
