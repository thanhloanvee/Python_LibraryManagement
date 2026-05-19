"""Review service."""
from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.review import Review, ReviewStatus
from app.repositories.review import ReviewRepository
from app.schemas.review import ReviewAdminUpdate, ReviewCreate, ReviewUpdate


class ReviewService:
    def __init__(self, db: AsyncSession) -> None:
        self._repo = ReviewRepository(db)

    async def get_or_404(self, review_id: int) -> Review:
        review = await self._repo.get_by_id(review_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found",
            )
        return review

    async def list_reviews(
        self,
        *,
        book_id=None,
        user_id=None,
        status=None,
        page=1,
        page_size=20,
    ):
        offset = (page - 1) * page_size
        return await self._repo.list_reviews(
            book_id=book_id,
            user_id=user_id,
            status=status,
            offset=offset,
            limit=page_size,
        )

    async def create_review(self, data: ReviewCreate, current_user_id: int) -> Review:
        # Check: user must have borrowed the book
        has_borrowed = await self._repo.user_has_borrowed_book(
            current_user_id, data.book_id
        )
        if not has_borrowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only review books you have borrowed.",
            )

        # Check: one review per user per book
        existing = await self._repo.get_by_user_and_book(
            current_user_id, data.book_id
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You have already reviewed this book.",
            )

        review = Review(
            book_id=data.book_id,
            user_id=current_user_id,
            rating=data.rating,
            comment=data.comment,
            status=ReviewStatus.ACTIVE,
        )
        return await self._repo.create(review)

    async def update_review(
        self, review_id: int, data: ReviewUpdate, current_user_id: int
    ) -> Review:
        review = await self.get_or_404(review_id)
        if review.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only edit your own reviews.",
            )
        if data.rating is not None:
            review.rating = data.rating
        if data.comment is not None:
            review.comment = data.comment
        return await self._repo.save(review)

    async def admin_update_review(
        self, review_id: int, data: ReviewAdminUpdate
    ) -> Review:
        review = await self.get_or_404(review_id)
        review.status = data.status
        return await self._repo.save(review)

    async def delete_review(
        self, review_id: int, current_user_id: int, is_admin: bool = False
    ) -> None:
        review = await self.get_or_404(review_id)
        if not is_admin and review.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own reviews.",
            )
        await self._repo.delete(review)

    async def get_average_rating(self, book_id: int) -> float:
        return await self._repo.get_average_rating(book_id)
