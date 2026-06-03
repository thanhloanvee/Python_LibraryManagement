"""User service — business logic for user management."""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import User, UserRole, UserStatus
from app.repositories.user import UserRepository
from app.schemas.user import UserAdminUpdate, UserCreate, UserUpdate
from app.services.base import BaseService


class UserService(BaseService):
    def __init__(self, db: AsyncSession) -> None:
        self._repo = UserRepository(db)

    async def get_or_404(self, user_id: int) -> User:
        user = await self._repo.get_by_id(user_id)
        return await super().get_or_404(user, "User")

    async def list_users(self, *, role=None, status=None, search=None, page=1, page_size=20):
        offset = self.calculate_offset(page, page_size)
        return await self._repo.list_users(
            role=role, status=status, search=search, offset=offset, limit=page_size
        )

    async def create_user(self, data: UserCreate) -> User:
        """Admin creates a user with explicit role."""
        if await self._repo.get_by_username(data.username):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Tên đăng nhập này đã được sử dụng.",
            )
        if await self._repo.get_by_email(data.email):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Địa chỉ email này đã được sử dụng.",
            )
        user = User(
            username=data.username,
            email=data.email,
            password_hash=hash_password(data.password),
            full_name=data.full_name,
            phone=data.phone,
            address=data.address,
            role=data.role,
            status=data.status,
        )
        return await self._repo.create(user)

    async def update_profile(self, user: User, data: UserUpdate) -> User:
        """User updates own non-sensitive profile fields."""
        if data.full_name is not None:
            user.full_name = data.full_name
        if data.phone is not None:
            user.phone = data.phone
        if data.address is not None:
            user.address = data.address
        if data.email is not None and data.email != user.email:
            existing = await self._repo.get_by_email(data.email)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Địa chỉ email này đã được sử dụng.",
                )
            user.email = data.email
        return await self._repo.save(user)

    async def admin_update_user(self, user_id: int, data: UserAdminUpdate) -> User:
        """Admin updates any user field including role and status."""
        user = await self.get_or_404(user_id)
        if data.full_name is not None:
            user.full_name = data.full_name
        if data.phone is not None:
            user.phone = data.phone
        if data.address is not None:
            user.address = data.address
        if data.email is not None and data.email != user.email:
            existing = await self._repo.get_by_email(data.email)
            if existing and existing.id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="This email address has already been taken.",
                )
            user.email = data.email
        if data.role is not None:
            user.role = data.role
        if data.status is not None:
            user.status = data.status
        return await self._repo.save(user)

    async def delete_user(self, user_id: int) -> None:
        user = await self.get_or_404(user_id)
        await self._repo.delete(user)
