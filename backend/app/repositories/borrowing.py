"""Borrowing repository."""
from __future__ import annotations

from datetime import date
from typing import List, Optional, Tuple

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.borrowing import Borrowing, BorrowingStatus
from app.models.book import Book
from app.models.user import User


class BorrowingRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, borrowing_id: int) -> Optional[Borrowing]:
        result = await self._db.execute(
            select(Borrowing)
            .options(
                selectinload(Borrowing.user),
                selectinload(Borrowing.book).selectinload(Book.category),
            )
            .where(Borrowing.id == borrowing_id)
        )
        return result.scalar_one_or_none()

    async def get_active_for_user_book(
        self, user_id: int, book_id: int
    ) -> Optional[Borrowing]:
        """Check if user already has an active borrowing for this book."""
        result = await self._db.execute(
            select(Borrowing).where(
                Borrowing.user_id == user_id,
                Borrowing.book_id == book_id,
                Borrowing.status.in_(
                    [BorrowingStatus.BORROWED, BorrowingStatus.OVERDUE]
                ),
            )
        )
        return result.scalar_one_or_none()

    async def count_active_for_user(self, user_id: int) -> int:
        """Count active borrowings for a user (used to enforce MAX_ACTIVE_BORROWINGS)."""
        result = await self._db.execute(
            select(func.count(Borrowing.id)).where(
                Borrowing.user_id == user_id,
                Borrowing.status.in_(
                    [BorrowingStatus.BORROWED, BorrowingStatus.OVERDUE]
                ),
            )
        )
        return result.scalar_one() or 0

    async def list_borrowings(
        self,
        *,
        user_id: Optional[int] = None,
        book_id: Optional[int] = None,
        status: Optional[BorrowingStatus] = None,
        overdue_only: bool = False,
        active_only: bool = False,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        offset: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Borrowing], int]:
        query = select(Borrowing).options(
            selectinload(Borrowing.user),
            selectinload(Borrowing.book),
        )
        count_query = select(func.count(Borrowing.id))

        filters = []
        if user_id is not None:
            filters.append(Borrowing.user_id == user_id)
        if book_id is not None:
            filters.append(Borrowing.book_id == book_id)
        if status is not None:
            filters.append(Borrowing.status == status)
        if active_only:
            filters.append(
                Borrowing.status.in_(
                    [BorrowingStatus.BORROWED, BorrowingStatus.OVERDUE]
                )
            )
        if overdue_only:
            filters.append(
                or_(
                    and_(
                        Borrowing.status == BorrowingStatus.BORROWED,
                        Borrowing.due_date < date.today(),
                    ),
                    Borrowing.status == BorrowingStatus.OVERDUE,
                )
            )

        if filters:
            query = query.where(*filters)
            count_query = count_query.where(*filters)

        # Apply sorting
        sort_column = {
            "created_at": Borrowing.created_at,
            "due_date": Borrowing.due_date,
            "borrow_date": Borrowing.borrow_date,
            "fine_amount": Borrowing.fine_amount,
        }.get(sort_by, Borrowing.created_at)

        sort_func = sort_column.desc() if sort_order == "desc" else sort_column.asc()

        total = (await self._db.execute(count_query)).scalar_one()
        items = (
            await self._db.execute(
                query.order_by(sort_func)
                .offset(offset)
                .limit(limit)
            )
        ).scalars().all()
        return list(items), total

    async def list_overdue(self) -> List[Borrowing]:
        """Return all currently overdue borrowings for bulk processing."""
        result = await self._db.execute(
            select(Borrowing)
            .options(selectinload(Borrowing.user), selectinload(Borrowing.book))
            .where(
                or_(
                    and_(
                        Borrowing.status == BorrowingStatus.BORROWED,
                        Borrowing.due_date < date.today(),
                    ),
                    Borrowing.status == BorrowingStatus.OVERDUE,
                )
            )
            .order_by(Borrowing.due_date.asc())
        )
        return list(result.scalars().all())

    async def create(self, borrowing: Borrowing) -> Borrowing:
        self._db.add(borrowing)
        await self._db.flush()
        await self._db.refresh(borrowing)
        return borrowing

    async def save(self, borrowing: Borrowing) -> Borrowing:
        self._db.add(borrowing)
        await self._db.flush()
        await self._db.refresh(borrowing)
        return borrowing
