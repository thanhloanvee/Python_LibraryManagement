"""Dashboard statistics service."""
from __future__ import annotations

from sqlalchemy import extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.book import Book
from app.models.borrowing import Borrowing, BorrowingStatus
from app.models.review import Review
from app.models.user import User, UserRole, UserStatus
from app.schemas.dashboard import (
    ActiveReader,
    BookInventoryItem,
    DashboardStats,
    MonthlyBorrowingStat,
    PopularBook,
)


class DashboardService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_stats(self) -> DashboardStats:
        """Aggregate KPIs for the admin dashboard."""
        total_books = (
            await self._db.execute(select(func.count(Book.id)))
        ).scalar_one()

        total_quantity = (
            await self._db.execute(select(func.coalesce(func.sum(Book.quantity), 0)))
        ).scalar_one()

        total_users = (
            await self._db.execute(
                select(func.count(User.id)).where(User.role == UserRole.READER)
            )
        ).scalar_one()

        total_borrowings = (
            await self._db.execute(select(func.count(Borrowing.id)))
        ).scalar_one()

        active_borrowings = (
            await self._db.execute(
                select(func.count(Borrowing.id)).where(
                    Borrowing.status.in_(
                        [BorrowingStatus.BORROWED, BorrowingStatus.OVERDUE]
                    )
                )
            )
        ).scalar_one()

        overdue_borrowings = (
            await self._db.execute(
                select(func.count(Borrowing.id)).where(
                    Borrowing.status == BorrowingStatus.OVERDUE
                )
            )
        ).scalar_one()

        fine_collected = (
            await self._db.execute(
                select(func.coalesce(func.sum(Borrowing.fine_amount), 0)).where(
                    Borrowing.fine_paid == True  # noqa: E712
                )
            )
        ).scalar_one()

        fine_outstanding = (
            await self._db.execute(
                select(func.coalesce(func.sum(Borrowing.fine_amount), 0)).where(
                    Borrowing.fine_paid == False,  # noqa: E712
                    Borrowing.fine_amount > 0,
                )
            )
        ).scalar_one()

        return DashboardStats(
            total_books=total_books,
            total_quantity=int(total_quantity),
            total_users=total_users,
            total_borrowings=total_borrowings,
            active_borrowings=active_borrowings,
            overdue_borrowings=overdue_borrowings,
            total_fine_collected=float(fine_collected),
            total_fine_outstanding=float(fine_outstanding),
        )

    async def get_book_inventory(self) -> list[BookInventoryItem]:
        """All books with their total and available quantity, low-stock first."""
        rows = (
            await self._db.execute(
                select(
                    Book.id,
                    Book.title,
                    Book.author,
                    Book.quantity,
                    Book.available_quantity,
                )
                .order_by(Book.available_quantity.asc(), Book.title.asc())
            )
        ).all()
        return [
            BookInventoryItem(
                id=row.id,
                title=row.title,
                author=row.author,
                quantity=row.quantity,
                available_quantity=row.available_quantity,
            )
            for row in rows
        ]

    async def get_popular_books(self, limit: int = 10) -> list[PopularBook]:
        """Top N books by borrow count."""
        rows = (
            await self._db.execute(
                select(
                    Book.id,
                    Book.title,
                    Book.author,
                    func.count(Borrowing.id).label("borrow_count"),
                )
                .outerjoin(Borrowing, Borrowing.book_id == Book.id)
                .group_by(Book.id)
                .order_by(func.count(Borrowing.id).desc())
                .limit(limit)
            )
        ).all()

        return [
            PopularBook(
                id=row.id,
                title=row.title,
                author=row.author,
                borrow_count=row.borrow_count or 0,
            )
            for row in rows
        ]

    async def get_active_readers(self, limit: int = 10) -> list[ActiveReader]:
        """Top N readers by borrow count."""
        rows = (
            await self._db.execute(
                select(
                    User.id,
                    User.username,
                    User.full_name,
                    func.count(Borrowing.id).label("borrow_count"),
                )
                .outerjoin(Borrowing, Borrowing.user_id == User.id)
                .where(User.role == UserRole.READER)
                .group_by(User.id)
                .order_by(func.count(Borrowing.id).desc())
                .limit(limit)
            )
        ).all()

        return [
            ActiveReader(
                id=row.id,
                username=row.username,
                full_name=row.full_name,
                borrow_count=row.borrow_count or 0,
            )
            for row in rows
        ]

    async def get_monthly_stats(self, year: int) -> list[MonthlyBorrowingStat]:
        """Monthly issued/returned counts for a given year."""
        month_names = [
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
        ]

        # Issued per month
        issued_rows = (
            await self._db.execute(
                select(
                    extract("month", Borrowing.borrow_date).label("month"),
                    func.count(Borrowing.id).label("count"),
                )
                .where(extract("year", Borrowing.borrow_date) == year)
                .group_by(extract("month", Borrowing.borrow_date))
            )
        ).all()

        # Returned per month
        returned_rows = (
            await self._db.execute(
                select(
                    extract("month", Borrowing.return_date).label("month"),
                    func.count(Borrowing.id).label("count"),
                )
                .where(
                    extract("year", Borrowing.return_date) == year,
                    Borrowing.return_date.isnot(None),
                )
                .group_by(extract("month", Borrowing.return_date))
            )
        ).all()

        issued_map = {int(r.month): int(r.count) for r in issued_rows}
        returned_map = {int(r.month): int(r.count) for r in returned_rows}

        return [
            MonthlyBorrowingStat(
                month=m,
                month_name=month_names[m - 1],
                issued=issued_map.get(m, 0),
                returned=returned_map.get(m, 0),
            )
            for m in range(1, 13)
        ]
