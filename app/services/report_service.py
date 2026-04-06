"""
ReportService — analytics and summary queries.
"""

from sqlalchemy.orm import Session

from app.repositories.book_repository import BookRepository
from app.repositories.borrow_repository import BorrowRepository
from app.repositories.user_repository import UserRepository


class ReportService:

    def __init__(self, db: Session) -> None:
        self._book_repo = BookRepository(db)
        self._borrow_repo = BorrowRepository(db)
        self._user_repo = UserRepository(db)

    def most_borrowed_books(self, limit: int = 10) -> list:
        rows = self._book_repo.get_most_borrowed(limit=limit)
        return [
            {**book.to_dict(), "borrow_count": count}
            for book, count in rows
        ]

    def overdue_books(self) -> list:
        records = self._borrow_repo.get_overdue_records()
        return [r.to_dict() for r in records]

    def active_members(self) -> list:
        members = self._user_repo.get_active_members()
        result = []
        for m in members:
            active = self._borrow_repo.active_borrow_count_for_user(m.id)
            if active > 0:
                data = m.to_dict()
                data["active_borrows"] = active
                result.append(data)
        return result

    def library_summary(self) -> dict:
        total_books = self._book_repo.total_count()
        all_borrows = self._borrow_repo.get_all_paginated(page=1, per_page=1)
        overdue_count = len(self._borrow_repo.get_overdue_records())
        all_users = self._user_repo.get_paginated(page=1, per_page=1)
        return {
            "total_books": total_books,
            "total_borrow_records": all_borrows["total"],
            "overdue_borrows": overdue_count,
            "total_users": all_users["total"],
        }
