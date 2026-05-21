"""Book repository."""
from __future__ import annotations

from typing import List, Optional, Tuple

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.book import Book, BookLanguage, BookStatus
from app.models.borrowing import Borrowing, BorrowingStatus
from app.utils import normalize_vi


class BookRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, book_id: int) -> Optional[Book]:
        result = await self._db.execute(
            select(Book)
            .options(selectinload(Book.category))
            .where(Book.id == book_id)
        )
        return result.scalar_one_or_none()

    async def get_by_isbn(self, isbn: str) -> Optional[Book]:
        result = await self._db.execute(
            select(Book).where(Book.isbn == isbn)
        )
        return result.scalar_one_or_none()

    async def list_books(
        self,
        *,
        title: Optional[str] = None,
        author: Optional[str] = None,
        isbn: Optional[str] = None,
        category_id: Optional[int] = None,
        status: Optional[BookStatus] = None,
        language: Optional[BookLanguage] = None,
        search: Optional[str] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Book], int]:
        """Filtered + paginated list."""
        query = select(Book).options(selectinload(Book.category))
        count_query = select(func.count(Book.id))

        if title:
            query = query.where(Book.title.ilike(f"%{title}%"))
            count_query = count_query.where(Book.title.ilike(f"%{title}%"))
        if author:
            query = query.where(Book.author.ilike(f"%{author}%"))
            count_query = count_query.where(Book.author.ilike(f"%{author}%"))
        if isbn:
            query = query.where(Book.isbn.ilike(f"%{isbn}%"))
            count_query = count_query.where(Book.isbn.ilike(f"%{isbn}%"))
        if category_id is not None:
            query = query.where(Book.category_id == category_id)
            count_query = count_query.where(Book.category_id == category_id)
        if status is not None:
            query = query.where(Book.status == status)
            count_query = count_query.where(Book.status == status)
        if language is not None:
            query = query.where(Book.language == language)
            count_query = count_query.where(Book.language == language)
        if search:
            like = f"%{search}%"
            norm_like = f"%{normalize_vi(search)}%"
            condition = or_(
                Book.title.ilike(like),
                Book.author.ilike(like),
                Book.isbn.ilike(like),
                func.normalize_vi(Book.title).like(norm_like),
                func.normalize_vi(Book.author).like(norm_like),
            )
            query = query.where(condition)
            count_query = count_query.where(condition)

        total = (await self._db.execute(count_query)).scalar_one()
        items = (
            await self._db.execute(
                query.order_by(Book.created_at.desc()).offset(offset).limit(limit)
            )
        ).scalars().all()
        return list(items), total

    async def has_active_borrowings(self, book_id: int) -> bool:
        """True when book has borrowings with status borrowed/overdue."""
        result = await self._db.execute(
            select(func.count(Borrowing.id))
            .where(Borrowing.book_id == book_id)
            .where(
                Borrowing.status.in_(
                    [BorrowingStatus.BORROWED, BorrowingStatus.OVERDUE]
                )
            )
        )
        return (result.scalar_one() or 0) > 0

    async def create(self, book: Book) -> Book:
        self._db.add(book)
        await self._db.flush()
        await self._db.refresh(book)
        return book

    async def save(self, book: Book) -> Book:
        self._db.add(book)
        await self._db.flush()
        await self._db.refresh(book)
        return book

    async def delete(self, book: Book) -> None:
        await self._db.delete(book)
        await self._db.flush()
