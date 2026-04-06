"""BorrowRecord and Fine repositories."""

from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models.borrow import BorrowRecord, Fine, BorrowStatusEnum
from app.repositories.base_repository import BaseRepository
from app.utils.pagination import paginate_query


class BorrowRepository(BaseRepository[BorrowRecord]):

    def __init__(self, db: Session) -> None:
        super().__init__(BorrowRecord, db)

    def get_active_by_user(self, user_id: int) -> List[BorrowRecord]:
        return self.db.execute(
            select(BorrowRecord).where(
                BorrowRecord.user_id == user_id,
                BorrowRecord.status == BorrowStatusEnum.BORROWED,
            )
        ).scalars().all()

    def get_active_borrow_for_book(
        self, user_id: int, book_id: int
    ) -> Optional[BorrowRecord]:
        return self.db.execute(
            select(BorrowRecord).where(
                BorrowRecord.user_id == user_id,
                BorrowRecord.book_id == book_id,
                BorrowRecord.status == BorrowStatusEnum.BORROWED,
            )
        ).scalar_one_or_none()

    def get_overdue_records(self) -> List[BorrowRecord]:
        now = datetime.now(timezone.utc)
        return self.db.execute(
            select(BorrowRecord).where(
                BorrowRecord.status == BorrowStatusEnum.BORROWED,
                BorrowRecord.due_date < now,
            )
        ).scalars().all()

    def get_user_history(self, user_id: int, page: int = 1, per_page: int = 20) -> dict:
        stmt = (
            select(BorrowRecord)
            .where(BorrowRecord.user_id == user_id)
            .order_by(BorrowRecord.borrow_date.desc())
        )
        return paginate_query(self.db, stmt, page, per_page)

    def get_all_paginated(self, page: int = 1, per_page: int = 20) -> dict:
        stmt = select(BorrowRecord).order_by(BorrowRecord.borrow_date.desc())
        return paginate_query(self.db, stmt, page, per_page)

    def active_borrow_count_for_user(self, user_id: int) -> int:
        return self.db.execute(
            select(func.count()).select_from(BorrowRecord).where(
                BorrowRecord.user_id == user_id,
                BorrowRecord.status == BorrowStatusEnum.BORROWED,
            )
        ).scalar_one()


class FineRepository(BaseRepository[Fine]):

    def __init__(self, db: Session) -> None:
        super().__init__(Fine, db)

    def get_by_borrow(self, borrow_id: int) -> Optional[Fine]:
        return self.db.execute(
            select(Fine).where(Fine.borrow_id == borrow_id)
        ).scalar_one_or_none()

    def get_unpaid_by_user(self, user_id: int) -> List[Fine]:
        return self.db.execute(
            select(Fine)
            .join(BorrowRecord, Fine.borrow_id == BorrowRecord.id)
            .where(
                BorrowRecord.user_id == user_id,
                Fine.is_paid == False,  # noqa: E712
            )
        ).scalars().all()
