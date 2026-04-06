"""User repository — all database queries related to users."""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.user import User, RoleEnum
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):

    def __init__(self, db: Session) -> None:
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.execute(
            select(User).where(User.email == email)
        ).scalar_one_or_none()

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.execute(
            select(User).where(User.username == username)
        ).scalar_one_or_none()

    def email_exists(self, email: str) -> bool:
        return self.get_by_email(email) is not None

    def username_exists(self, username: str) -> bool:
        return self.get_by_username(username) is not None

    def get_active_members(self) -> List[User]:
        return self.db.execute(
            select(User).where(User.is_active == True, User.role == RoleEnum.MEMBER)  # noqa: E712
        ).scalars().all()

    def get_paginated(self, page: int = 1, per_page: int = 20) -> dict:
        from app.utils.pagination import paginate_query
        stmt = select(User).order_by(User.created_at.desc())
        return paginate_query(self.db, stmt, page, per_page)
