"""Admin dashboard."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.dashboard import DashboardService
from app.web.dependencies import require_admin
from app.web.templating import render

router = APIRouter()


@router.get("/admin/dashboard")
async def dashboard(
    request: Request,
    year: int | None = None,
    inventory_page: int = 1,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_admin),
):
    import datetime
    current_year = year or datetime.date.today().year
    svc = DashboardService(db)
    stats = await svc.get_stats()
    popular = await svc.get_popular_books(limit=5)
    active_readers = await svc.get_active_readers(limit=5)
    monthly = await svc.get_monthly_stats(year=current_year)
    book_inventory, inventory_total = await svc.get_book_inventory(
        page=inventory_page, page_size=10
    )

    return render(
        "admin/dashboard.html",
        {
            "stats": stats,
            "popular_books": popular,
            "active_readers": active_readers,
            "monthly_stats": monthly,
            "current_year": current_year,
            "today_year": datetime.date.today().year,
            "book_inventory": book_inventory,
            "inventory_page": inventory_page,
            "inventory_total": inventory_total,
            "inventory_page_size": 10,
        },
        request,
    )
