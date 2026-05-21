"""Review repository."""
from __future__ import annotations

from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.borrowing import Borrowing
from app.models.review import Review, ReviewStatus


class ReviewRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, review_id: int) -> Optional[Review]:
        result = await self._db.execute(
            select(Review)
            .options(selectinload(Review.user))
            .where(Review.id == review_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_and_book(
        self, user_id: int, book_id: int
    ) -> Optional[Review]:
        """Check for existing review (unique constraint guard)."""
        result = await self._db.execute(
            select(Review).where(
                Review.user_id == user_id, Review.book_id == book_id
            )
        )
        return result.scalar_one_or_none()

    async def user_has_borrowed_book(self, user_id: int, book_id: int) -> bool:
        """True if user has ever borrowed this book."""
        result = await self._db.execute(
            select(func.count(Borrowing.id)).where(
                Borrowing.user_id == user_id, Borrowing.book_id == book_id
            )
        )
        return (result.scalar_one() or 0) > 0

    async def list_reviews(
        self,
        *,
        book_id: Optional[int] = None,
        user_id: Optional[int] = None,
        status: Optional[ReviewStatus] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Review], int]:
        query = select(Review).options(selectinload(Review.user))
        count_query = select(func.count(Review.id))

        filters = []
        if book_id is not None:
            filters.append(Review.book_id == book_id)
        if user_id is not None:
            filters.append(Review.user_id == user_id)
        if status is not None:
            filters.append(Review.status == status)

        if filters:
            query = query.where(*filters)
            count_query = count_query.where(*filters)

        total = (await self._db.execute(count_query)).scalar_one()
        items = (
            await self._db.execute(
                query.order_by(Review.created_at.desc())
                .offset(offset)
                .limit(limit)
            )
        ).scalars().all()
        return list(items), total

    async def get_average_rating(self, book_id: int) -> float:
        result = await self._db.execute(
            select(func.avg(Review.rating)).where(
                Review.book_id == book_id,
                Review.status == ReviewStatus.ACTIVE,
            )
        )
        avg = result.scalar_one_or_none()
        return round(float(avg), 2) if avg is not None else 0.0

    async def create(self, review: Review) -> Review:
        self._db.add(review)
        await self._db.flush()
        await self._db.refresh(review)
        return review

    async def save(self, review: Review) -> Review:
        self._db.add(review)
        await self._db.flush()
        await self._db.refresh(review)
        return review

    async def delete(self, review: Review) -> None:
        await self._db.delete(review)
        await self._db.flush()
