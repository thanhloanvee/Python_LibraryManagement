"""User repository."""
from __future__ import annotations

from typing import List, Optional, Tuple

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole, UserStatus
from app.utils import normalize_vi


class UserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self._db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self._db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self._db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def list_users(
        self,
        *,
        role: Optional[UserRole] = None,
        status: Optional[UserStatus] = None,
        search: Optional[str] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> Tuple[List[User], int]:
        """Return (items, total_count) with optional filters."""
        query = select(User)
        count_query = select(func.count(User.id))

        if role is not None:
            query = query.where(User.role == role)
            count_query = count_query.where(User.role == role)
        if status is not None:
            query = query.where(User.status == status)
            count_query = count_query.where(User.status == status)
        if search:
            like = f"%{search}%"
            norm_like = f"%{normalize_vi(search)}%"
            condition = or_(
                User.username.ilike(like),
                User.full_name.ilike(like),
                User.email.ilike(like),
                func.normalize_vi(User.username).like(norm_like),
                func.normalize_vi(User.full_name).like(norm_like),
            )
            query = query.where(condition)
            count_query = count_query.where(condition)

        total = (await self._db.execute(count_query)).scalar_one()
        items = (
            await self._db.execute(
                query.order_by(User.created_at.desc()).offset(offset).limit(limit)
            )
        ).scalars().all()
        return list(items), total

    async def create(self, user: User) -> User:
        self._db.add(user)
        await self._db.flush()
        await self._db.refresh(user)
        return user

    async def save(self, user: User) -> User:
        self._db.add(user)
        await self._db.flush()
        await self._db.refresh(user)
        return user

    async def delete(self, user: User) -> None:
        await self._db.delete(user)
        await self._db.flush()
