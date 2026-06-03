"""Dashboard statistics service."""
from __future__ import annotations

from datetime import date

from sqlalchemy import Float, Integer, and_, extract, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
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

settings = get_settings()


class DashboardService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_stats(self) -> DashboardStats:
        """Aggregate KPIs for the admin dashboard — 3 focused queries instead of 8."""
        from sqlalchemy import case

        # Query 1: Book inventory
        book_result = await self._db.execute(
            select(
                func.count(Book.id).label("total_books"),
                func.coalesce(func.sum(Book.available_quantity), 0).label("total_quantity"),
            )
        )
        book_row = book_result.one()

        # Query 2: User count
        user_result = await self._db.execute(
            select(func.count(User.id)).where(User.role == UserRole.READER)
        )
        total_users = user_result.scalar_one()

        # Query 3: All borrowing KPIs in one pass
        # Note: overdue includes (BORROWED with due_date < today) OR (OVERDUE)
        today = date.today()
        overdue_condition = or_(
            and_(
                Borrowing.status == BorrowingStatus.BORROWED,
                Borrowing.due_date < today,
            ),
            Borrowing.status == BorrowingStatus.OVERDUE,
        )

        borrow_result = await self._db.execute(
            select(
                func.count(Borrowing.id).label("total_borrowings"),
                func.sum(
                    case(
                        (
                            Borrowing.status.in_(
                                [BorrowingStatus.BORROWED, BorrowingStatus.OVERDUE]
                            ),
                            1,
                        ),
                        else_=0,
                    )
                ).label("active_borrowings"),
                func.sum(
                    case(
                        (overdue_condition, 1),
                        else_=0,
                    )
                ).label("overdue_borrowings"),
                func.coalesce(
                    func.sum(
                        case(
                            (Borrowing.fine_paid == True, Borrowing.fine_amount),  # noqa: E712
                            else_=0,
                        )
                    ),
                    0,
                ).label("fine_collected"),
                func.coalesce(
                    func.sum(
                        func.cast(
                            case(
                                # For overdue unreturned (BORROWED past due or OVERDUE): calculate dynamically
                                (
                                    overdue_condition
                                    & (Borrowing.fine_paid == False),  # noqa: E712
                                    func.cast(
                                        func.cast(
                                            func.julianday(func.date("now")) - func.julianday(Borrowing.due_date),
                                            Integer
                                        ) * settings.fine_per_day,
                                        Float
                                    ),
                                ),
                                else_=0.0,
                            ),
                            Float
                        )
                    ),
                    0.0,
                ).label("fine_outstanding"),
            )
        )
        borrow_row = borrow_result.one()

        return DashboardStats(
            total_books=book_row.total_books or 0,
            total_quantity=int(book_row.total_quantity or 0),
            total_users=total_users or 0,
            total_borrowings=borrow_row.total_borrowings or 0,
            active_borrowings=borrow_row.active_borrowings or 0,
            overdue_borrowings=borrow_row.overdue_borrowings or 0,
            total_fine_collected=float(borrow_row.fine_collected or 0),
            total_fine_outstanding=float(borrow_row.fine_outstanding or 0),
        )

    async def get_book_inventory(
        self, page: int = 1, page_size: int = 10
    ) -> tuple[list[BookInventoryItem], int]:
        """All books with their total and available quantity, low-stock first."""
        offset = (page - 1) * page_size

        # Get total count
        count_result = await self._db.execute(
            select(func.count(Book.id))
        )
        total = count_result.scalar_one() or 0

        # Get paginated results
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
                .offset(offset)
                .limit(page_size)
            )
        ).all()

        items = [
            BookInventoryItem(
                id=row.id,
                title=row.title,
                author=row.author,
                quantity=row.quantity,
                available_quantity=row.available_quantity,
            )
            for row in rows
        ]
        return items, total

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
