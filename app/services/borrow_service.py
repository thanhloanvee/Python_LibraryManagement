"""
BorrowService — borrow/return workflow and fine calculation.

Business rules:
  - User cannot exceed MAX_BORROW_LIMIT concurrent borrows
  - Book must have available_quantity > 0
  - Fine = overdue_days * FINE_PER_DAY stored in fines table
  - available_quantity is updated inside a single DB transaction
"""

import logging
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.borrow import BorrowRecord, BorrowStatusEnum, Fine
from app.repositories.borrow_repository import BorrowRepository, FineRepository
from app.repositories.book_repository import BookRepository
from app.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


class BorrowService:

    def __init__(self, db: Session) -> None:
        self._borrow_repo = BorrowRepository(db)
        self._fine_repo = FineRepository(db)
        self._book_repo = BookRepository(db)
        self._user_repo = UserRepository(db)

    def borrow_book(self, user_id: int, book_id: int) -> BorrowRecord:
        settings = get_settings()
        user = self._user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise ValueError("User not found or account is deactivated.")

        book = self._book_repo.get_by_id(book_id)
        if not book:
            raise ValueError(f"Book with id={book_id} not found.")
        if not book.is_available:
            raise ValueError(f"'{book.title}' is not currently available.")

        active_count = self._borrow_repo.active_borrow_count_for_user(user_id)
        if active_count >= settings.MAX_BORROW_LIMIT:
            raise ValueError(
                f"Borrow limit reached ({settings.MAX_BORROW_LIMIT} books). Please return a book first."
            )

        now = datetime.now(timezone.utc)
        due_date = now + timedelta(days=settings.BORROW_PERIOD_DAYS)
        try:
            record = BorrowRecord(
                user_id=user_id,
                book_id=book_id,
                borrow_date=now,
                due_date=due_date,
                status=BorrowStatusEnum.BORROWED,
            )
            self._borrow_repo.add(record)
            book.decrement_stock()
            self._borrow_repo.commit()
            logger.info("User %d borrowed book %d (due %s)", user_id, book_id, due_date.date())
            return record
        except Exception:
            self._borrow_repo.rollback()
            raise

    def return_book(self, borrow_id: int, user_id: int) -> BorrowRecord:
        settings = get_settings()
        record = self._borrow_repo.get_by_id(borrow_id)
        if not record:
            raise ValueError(f"Borrow record id={borrow_id} not found.")
        if record.user_id != user_id:
            raise ValueError("You can only return books that you borrowed.")
        if record.status == BorrowStatusEnum.RETURNED:
            raise ValueError("This book has already been returned.")

        now = datetime.now(timezone.utc)
        try:
            # Calculate fine BEFORE changing status (is_overdue() checks status == BORROWED)
            overdue_days = record.overdue_days_at_return(now)
            fine_amount = round(overdue_days * settings.FINE_PER_DAY, 2)

            record.return_date = now
            record.status = BorrowStatusEnum.RETURNED

            if fine_amount > 0:
                fine = Fine(
                    borrow_id=record.id,
                    overdue_days=overdue_days,
                    amount=Decimal(str(fine_amount)),
                )
                self._fine_repo.add(fine)
                logger.info(
                    "Fine created: borrow_id=%d overdue=%d days amount=%.2f",
                    record.id, overdue_days, fine_amount,
                )

            record.book.increment_stock()
            self._borrow_repo.commit()
            logger.info("User %d returned book %d", user_id, record.book_id)
            return record
        except Exception:
            self._borrow_repo.rollback()
            raise

    def _calculate_fine(self, record: BorrowRecord, fine_per_day: float) -> float:
        return round(record.overdue_days() * fine_per_day, 2)

    def get_user_borrows(self, user_id: int, page: int = 1, per_page: int = 20) -> dict:
        return self._borrow_repo.get_user_history(user_id, page=page, per_page=per_page)

    def get_all_borrows(self, page: int = 1, per_page: int = 20) -> dict:
        return self._borrow_repo.get_all_paginated(page=page, per_page=per_page)

    def get_overdue_borrows(self):
        return self._borrow_repo.get_overdue_records()
