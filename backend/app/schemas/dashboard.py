"""Dashboard / statistics schemas."""
from __future__ import annotations

from pydantic import BaseModel


class DashboardStats(BaseModel):
    """Top-level KPIs shown on the admin dashboard."""

    total_books: int
    total_users: int
    total_borrowings: int
    active_borrowings: int
    overdue_borrowings: int
    total_fine_collected: float
    total_fine_outstanding: float


class MonthlyBorrowingStat(BaseModel):
    """Issued/returned counts per month."""

    month: int       # 1–12
    month_name: str  # "Jan" … "Dec"
    issued: int
    returned: int


class PopularBook(BaseModel):
    """A book with its borrow count."""

    id: int
    title: str
    author: str
    borrow_count: int


class ActiveReader(BaseModel):
    """A reader with their borrow count."""

    id: int
    username: str
    full_name: str
    borrow_count: int
