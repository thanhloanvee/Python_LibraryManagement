"""Book repository — all database queries related to books."""

from typing import Optional, List
from sqlalchemy import select, or_, func
from sqlalchemy.orm import Session
from app.models.book import Book
from app.repositories.base_repository import BaseRepository
from app.utils.pagination import paginate_query


class BookRepository(BaseRepository[Book]):

    def __init__(self, db: Session) -> None:
        super().__init__(Book, db)

    def get_by_isbn(self, isbn: str) -> Optional[Book]:
        return self.db.execute(
            select(Book).where(Book.isbn == isbn)
        ).scalar_one_or_none()

    def search(self, query: str, category: str = None, page: int = 1, per_page: int = 20) -> dict:
        """Full-text search across title and author; optional category filter."""
        stmt = select(Book)
        if query:
            like = f"%{query}%"
            stmt = stmt.where(
                or_(
                    Book.title.ilike(like),
                    Book.author.ilike(like),
                )
            )
        if category:
            stmt = stmt.where(Book.category.ilike(f"%{category}%"))
        stmt = stmt.order_by(Book.title)
        return paginate_query(self.db, stmt, page, per_page)

    def get_available(self) -> List[Book]:
        return self.db.execute(
            select(Book).where(Book.available_quantity > 0)
        ).scalars().all()

    def get_most_borrowed(self, limit: int = 10) -> List:
        """Returns (Book, borrow_count) tuples ordered by popularity."""
        from app.models.borrow import BorrowRecord
        return self.db.execute(
            select(Book, func.count(BorrowRecord.id).label("borrow_count"))
            .join(BorrowRecord, Book.id == BorrowRecord.book_id)
            .group_by(Book.id)
            .order_by(func.count(BorrowRecord.id).desc())
            .limit(limit)
        ).all()

    def total_count(self) -> int:
        return self.db.execute(
            select(func.count()).select_from(Book)
        ).scalar_one()
