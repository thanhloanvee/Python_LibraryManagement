"""
UserService — admin-level user management operations.
"""

import logging
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.repositories.borrow_repository import BorrowRepository

logger = logging.getLogger(__name__)


class UserService:

    def __init__(self, db: Session) -> None:
        self._user_repo = UserRepository(db)
        self._borrow_repo = BorrowRepository(db)

    def get_all_users(self, page: int = 1, per_page: int = 20) -> dict:
        return self._user_repo.get_paginated(page=page, per_page=per_page)

    def get_user_by_id(self, user_id: int) -> User:
        user = self._user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with id={user_id} not found.")
        return user

    def set_active_status(self, user_id: int, is_active: bool) -> User:
        user = self.get_user_by_id(user_id)
        user.is_active = is_active
        self._user_repo.commit()
        logger.info("User %s %s.", user.username, "activated" if is_active else "deactivated")
        return user

    def delete_user(self, user_id: int) -> None:
        user = self.get_user_by_id(user_id)
        active_borrows = self._borrow_repo.active_borrow_count_for_user(user_id)
        if active_borrows > 0:
            raise ValueError(
                f"Cannot delete user '{user.username}': they have {active_borrows} active borrow(s)."
            )
        self._user_repo.delete(user)
        self._user_repo.commit()
        logger.info("User %s deleted.", user.username)
