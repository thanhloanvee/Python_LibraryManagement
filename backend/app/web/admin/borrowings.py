"""Admin borrowing management."""
from __future__ import annotations

import datetime

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.borrowing import BorrowingStatus
from app.schemas.borrowing import BorrowingFilter, BorrowingCreate, ReturnBookRequest
from app.services.borrowing import BorrowingService
from app.services.book import BookService
from app.services.user import UserService
from app.web.dependencies import require_librarian
from app.web.templating import render, set_flash

router = APIRouter()


@router.get("/admin/borrowings")
async def borrowings_index(
    request: Request,
    user_id: int | None = None,
    book_id: int | None = None,
    status: str | None = None,
    overdue_only: bool = False,
    page: int = 1,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_librarian),
):
    filters = BorrowingFilter(
        user_id=user_id,
        book_id=book_id,
        status=BorrowingStatus(status) if status else None,
        overdue_only=overdue_only,
    )
    borrowings, total = await BorrowingService(db).list_borrowings(
        filters, page=page, page_size=20
    )
    ctx = {
        "borrowings": borrowings,
        "total": total,
        "page": page,
        "page_size": 20,
        "filters": {
            "user_id": user_id,
            "book_id": book_id,
            "status": status,
            "overdue_only": overdue_only,
        },
        "statuses": list(BorrowingStatus),
    }
    if request.headers.get("HX-Request"):
        return render("admin/borrowings/_rows.html", ctx, request)
    return render("admin/borrowings/index.html", ctx, request)


@router.get("/admin/borrowings/issue")
async def issue_form(
    request: Request,
    book_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_librarian),
):
    book = None
    if book_id:
        book = await BookService(db).get_or_404(book_id)
    due_default = (
        datetime.date.today() + datetime.timedelta(days=14)
    ).isoformat()
    return render(
        "admin/borrowings/issue.html",
        {"preselected_book": book, "due_default": due_default},
        request,
    )


@router.post("/admin/borrowings/issue")
async def issue_submit(
    request: Request,
    user_id: int = Form(...),
    book_id: int = Form(...),
    due_date: str = Form(...),
    librarian_notes: str = Form(default=""),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_librarian),
):
    try:
        due = datetime.date.fromisoformat(due_date)
        payload = BorrowingCreate(
            user_id=user_id,
            book_id=book_id,
            due_date=datetime.datetime.combine(due, datetime.time.min),
            librarian_notes=librarian_notes or None,
        )
        borrowing = await BorrowingService(db).issue_book(payload, current_user.id)
        resp = RedirectResponse(url="/admin/borrowings", status_code=302)
        set_flash(resp, f"Book issued — borrowing #{borrowing.id}.", "success")
        return resp
    except Exception as exc:
        due_default = (
            datetime.date.today() + datetime.timedelta(days=14)
        ).isoformat()
        return render(
            "admin/borrowings/issue.html",
            {
                "error": str(exc.detail if hasattr(exc, "detail") else exc),
                "due_default": due_default,
            },
            request,
        )


@router.get("/admin/borrowings/{borrowing_id}")
async def borrowing_detail(
    borrowing_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_librarian),
):
    borrowing = await BorrowingService(db).get_or_404(borrowing_id)
    return render("admin/borrowings/detail.html", {"borrowing": borrowing}, request)


@router.get("/admin/borrowings/{borrowing_id}/return")
async def return_form(
    borrowing_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_librarian),
):
    borrowing = await BorrowingService(db).get_or_404(borrowing_id)
    return render(
        "admin/borrowings/return.html",
        {"borrowing": borrowing},
        request,
    )


@router.post("/admin/borrowings/{borrowing_id}/return")
async def return_submit(
    borrowing_id: int,
    request: Request,
    book_condition: str = Form(...),
    librarian_notes: str = Form(default=""),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_librarian),
):
    try:
        from app.models.borrowing import BookCondition
        payload = ReturnBookRequest(
            book_condition=BookCondition(book_condition),
            librarian_notes=librarian_notes or None,
        )
        borrowing = await BorrowingService(db).return_book(borrowing_id, payload)
        resp = RedirectResponse(url="/admin/borrowings", status_code=302)
        set_flash(
            resp,
            f"Book returned — fine: {borrowing.fine_amount:,.0f} VND.",
            "success",
        )
        return resp
    except Exception as exc:
        borrowing = await BorrowingService(db).get_or_404(borrowing_id)
        return render(
            "admin/borrowings/return.html",
            {
                "borrowing": borrowing,
                "error": str(exc.detail if hasattr(exc, "detail") else exc),
            },
            request,
        )


@router.post("/admin/borrowings/{borrowing_id}/mark-fine-paid")
async def mark_fine_paid(
    borrowing_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_librarian),
):
    from app.schemas.borrowing import MarkFinePaidRequest
    await BorrowingService(db).mark_fine_paid(borrowing_id, MarkFinePaidRequest())
    resp = RedirectResponse(url=f"/admin/borrowings/{borrowing_id}", status_code=302)
    set_flash(resp, "Fine marked as paid.", "success")
    return resp
