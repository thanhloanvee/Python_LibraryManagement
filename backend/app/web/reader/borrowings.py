"""Reader borrowing views."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.borrowing import BorrowingFilter
from app.services.borrowing import BorrowingService
from app.web.dependencies import require_reader
from app.web.templating import render, set_flash

router = APIRouter()


@router.get("/reader/my-books")
async def my_books(
    request: Request,
    page: int = 1,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_reader),
):
    """Active/current borrowings for the logged-in reader."""
    borrowings, total = await BorrowingService(db).list_borrowings(
        BorrowingFilter(user_id=user.id, active_only=True),
        page=page,
        page_size=10,
    )
    return render(
        "reader/my_books.html",
        {"borrowings": borrowings, "total": total, "page": page, "page_size": 10},
        request,
    )


@router.get("/reader/history")
async def borrowing_history(
    request: Request,
    page: int = 1,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_reader),
):
    """Full borrowing history for the logged-in reader."""
    borrowings, total = await BorrowingService(db).list_borrowings(
        BorrowingFilter(user_id=user.id),
        page=page,
        page_size=15,
    )
    return render(
        "reader/history.html",
        {"borrowings": borrowings, "total": total, "page": page, "page_size": 15},
        request,
    )


@router.post("/reader/borrowings/{borrowing_id}/renew")
async def renew_borrowing(
    borrowing_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_reader),
):
    try:
        from app.schemas.borrowing import RenewBorrowingRequest
        svc = BorrowingService(db)
        b = await svc.get_or_404(borrowing_id)
        if b.user_id != user.id:
            raise PermissionError("Not your borrowing.")
        updated = await svc.renew_borrowing(borrowing_id, RenewBorrowingRequest())
        resp = RedirectResponse(url="/reader/my-books", status_code=302)
        set_flash(
            resp,
            f"Borrowing renewed — new due date: {updated.due_date.strftime('%d/%m/%Y')}.",
            "success",
        )
        return resp
    except Exception as exc:
        resp = RedirectResponse(url="/reader/my-books", status_code=302)
        set_flash(resp, str(exc.detail if hasattr(exc, "detail") else exc), "error")
        return resp
