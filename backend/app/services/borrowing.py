"""Borrowing service — core circulation business logic."""
from __future__ import annotations

from datetime import date, timedelta

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.borrowing import Borrowing, BorrowingStatus
from app.models.user import UserRole
from app.repositories.book import BookRepository
from app.repositories.borrowing import BorrowingRepository
from app.repositories.user import UserRepository
from app.schemas.borrowing import (
    BorrowingCreate,
    BorrowingFilter,
    RenewBorrowingRequest,
    ReturnBookRequest,
)

settings = get_settings()


class BorrowingService:
    def __init__(self, db: AsyncSession) -> None:
        self._repo = BorrowingRepository(db)
        self._book_repo = BookRepository(db)
        self._user_repo = UserRepository(db)

    async def get_or_404(self, borrowing_id: int) -> Borrowing:
        borrowing = await self._repo.get_by_id(borrowing_id)
        if not borrowing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Borrowing record not found",
            )
        return borrowing

    async def list_borrowings(
        self,
        filters: BorrowingFilter,
        *,
        page: int = 1,
        page_size: int = 20,
    ):
        offset = (page - 1) * page_size
        return await self._repo.list_borrowings(
            user_id=filters.user_id,
            book_id=filters.book_id,
            status=filters.status,
            overdue_only=filters.overdue_only,
            active_only=filters.active_only,
            offset=offset,
            limit=page_size,
        )

    async def issue_book(self, data: BorrowingCreate) -> Borrowing:
        """
        Librarian issues a book to a reader.

        Raises HTTP 422 on any business-rule violation.
        """
        # 1. Validate user exists and is active
        user = await self._user_repo.get_by_id(data.user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Reader not found or inactive.",
            )

        # 2. Validate book exists
        book = await self._book_repo.get_by_id(data.book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Book not found.",
            )

        # 3. Check availability (snapshot — final atomic check happens at step 7)
        if not book.is_available:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "Book is not available for borrowing "
                    f"(status={book.status.value}, "
                    f"available_quantity={book.available_quantity})."
                ),
            )

        # 4. Check MAX_ACTIVE_BORROWINGS per user
        active_count = await self._repo.count_active_for_user(data.user_id)
        if active_count >= settings.max_active_borrowings:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"Reader already has {active_count} active borrowings "
                    f"(maximum is {settings.max_active_borrowings})."
                ),
            )

        # 5. Check user doesn't already have this book
        existing = await self._repo.get_active_for_user_book(
            data.user_id, data.book_id
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Reader already has an active borrowing for this book.",
            )

        # 6. Compute dates
        borrow_date = date.today()
        due_date = data.due_date or (
            borrow_date + timedelta(days=settings.borrowing_period_days)
        )

        if due_date <= borrow_date:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="due_date must be after borrow_date.",
            )

        # 7. Atomic decrement — prevents concurrent over-issue
        decremented = await self._book_repo.decrement_available(data.book_id)
        if not decremented:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Book is no longer available (just taken by another request).",
            )

        # 8. Create borrowing record
        borrowing = Borrowing(
            user_id=data.user_id,
            book_id=data.book_id,
            borrow_date=borrow_date,
            due_date=due_date,
            status=BorrowingStatus.BORROWED,
            renewed_count=0,
            fine_amount=0.0,
            fine_paid=False,
            librarian_notes=data.librarian_notes,
        )
        return await self._repo.create(borrowing)

    async def return_book(
        self, borrowing_id: int, data: ReturnBookRequest
    ) -> Borrowing:
        """
        Process a book return. Calculates fine if overdue.
        """
        borrowing = await self.get_or_404(borrowing_id)

        if borrowing.status == BorrowingStatus.RETURNED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This book has already been returned.",
            )

        # Calculate fine before updating status
        fine = borrowing.calculate_fine(settings.fine_per_day)

        # Update borrowing record
        borrowing.return_date = date.today()
        borrowing.status = BorrowingStatus.RETURNED
        borrowing.fine_amount = fine
        if data.book_condition is not None:
            borrowing.book_condition = data.book_condition
        if data.librarian_notes is not None:
            borrowing.librarian_notes = data.librarian_notes

        # Increment available_quantity
        book = await self._book_repo.get_by_id(borrowing.book_id)
        if book:
            book.available_quantity += 1
            await self._book_repo.save(book)

        return await self._repo.save(borrowing)

    async def renew_borrowing(
        self,
        borrowing_id: int,
        data: RenewBorrowingRequest,
        requesting_user_id: int | None = None,
        requesting_role: UserRole = UserRole.READER,
    ) -> Borrowing:
        borrowing = await self.get_or_404(borrowing_id)

        if requesting_role == UserRole.READER and requesting_user_id is not None:
            if borrowing.user_id != requesting_user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only renew your own borrowings.",
                )

        if borrowing.status not in (BorrowingStatus.BORROWED, BorrowingStatus.OVERDUE):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Only active borrowings can be renewed.",
            )

        if borrowing.renewed_count >= settings.max_renewals:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"Maximum renewals ({settings.max_renewals}) reached "
                    "for this borrowing."
                ),
            )

        borrowing.due_date = borrowing.due_date + timedelta(days=data.extend_days)
        borrowing.renewed_count += 1

        return await self._repo.save(borrowing)

    async def mark_fine_paid(self, borrowing_id: int) -> Borrowing:
        borrowing = await self.get_or_404(borrowing_id)
        borrowing.fine_paid = True
        return await self._repo.save(borrowing)

    async def sync_overdue_statuses(self) -> int:
        """
        Flip status → OVERDUE for all past-due active borrowings.
        Can be called by a scheduled background task.
        Returns count of records updated.
        """
        overdue = await self._repo.list_overdue()
        count = 0
        for b in overdue:
            if b.status != BorrowingStatus.OVERDUE:
                b.status = BorrowingStatus.OVERDUE
                b.fine_amount = b.calculate_fine(settings.fine_per_day)
                await self._repo.save(b)
                count += 1
        return count
