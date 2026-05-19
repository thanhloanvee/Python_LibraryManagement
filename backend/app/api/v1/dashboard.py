"""
Dashboard router.

All endpoints are Admin-only.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.rbac import require_admin
from app.schemas.dashboard import (
    ActiveReader,
    DashboardStats,
    MonthlyBorrowingStat,
    PopularBook,
)
from app.services.dashboard import DashboardService

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
    dependencies=[Depends(require_admin)],
)


@router.get(
    "/stats",
    response_model=DashboardStats,
    summary="Get dashboard KPIs (Admin)",
)
async def get_stats(
    db: AsyncSession = Depends(get_db),
) -> DashboardStats:
    """Aggregate statistics for the admin dashboard."""
    service = DashboardService(db)
    return await service.get_stats()


@router.get(
    "/popular-books",
    response_model=list[PopularBook],
    summary="Top books by borrow count (Admin)",
)
async def popular_books(
    limit: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
) -> list[PopularBook]:
    service = DashboardService(db)
    return await service.get_popular_books(limit=limit)


@router.get(
    "/active-readers",
    response_model=list[ActiveReader],
    summary="Top readers by borrow count (Admin)",
)
async def active_readers(
    limit: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
) -> list[ActiveReader]:
    service = DashboardService(db)
    return await service.get_active_readers(limit=limit)


@router.get(
    "/monthly-stats",
    response_model=list[MonthlyBorrowingStat],
    summary="Monthly borrowing statistics (Admin)",
)
async def monthly_stats(
    year: int = Query(default=2026, ge=2000, le=2100),
    db: AsyncSession = Depends(get_db),
) -> list[MonthlyBorrowingStat]:
    service = DashboardService(db)
    return await service.get_monthly_stats(year=year)
