"""
Borrowings router.

RBAC matrix:
  GET /borrowings                    → Librarian/Admin (all); Reader (own only)
  GET /borrowings/{id}               → Librarian/Admin or owner
  POST /borrowings                   → Librarian/Admin (issue)
  POST /borrowings/{id}/return       → Librarian/Admin
  POST /borrowings/{id}/renew        → Authenticated (Reader for own, Librarian for any)
  POST /borrowings/{id}/mark-fine-paid → Librarian/Admin
  POST /borrowings/sync-overdue      → Admin (background trigger)
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import get_current_active_user
from app.dependencies.rbac import require_admin, require_librarian, require_reader
from app.models.borrowing import BorrowingStatus
from app.models.user import User, UserRole
from app.schemas.borrowing import (
    BorrowingCreate,
    BorrowingFilter,
    BorrowingRead,
    MarkFinePaidRequest,
    RenewBorrowingRequest,
    ReturnBookRequest,
)
from app.schemas.common import MessageResponse, PaginatedResponse
from app.services.borrowing import BorrowingService
from app.utils.pagination import Paginator, make_paginated_response

router = APIRouter(prefix="/borrowings", tags=["Borrowings"])


def _borrowing_to_read(b) -> BorrowingRead:
    """Populate computed fields (is_overdue, days_overdue, days_until_due)."""
    data = {
        "id": b.id,
        "user_id": b.user_id,
        "book_id": b.book_id,
        "user": b.user,
        "book": b.book,
        "borrow_date": b.borrow_date,
        "due_date": b.due_date,
        "return_date": b.return_date,
        "status": b.status,
        "book_condition": b.book_condition,
        "renewed_count": b.renewed_count,
        "fine_amount": b.fine_amount,
        "fine_paid": b.fine_paid,
        "librarian_notes": b.librarian_notes,
        "is_overdue": b.is_overdue,
        "days_overdue": b.days_overdue,
        "days_until_due": b.days_until_due,
        "created_at": b.created_at,
        "updated_at": b.updated_at,
    }
    return BorrowingRead.model_validate(data)


@router.get(
    "",
    response_model=PaginatedResponse[BorrowingRead],
    summary="List borrowings",
)
async def list_borrowings(
    status_filter: BorrowingStatus | None = Query(default=None, alias="status"),
    user_id: int | None = Query(default=None),
    book_id: int | None = Query(default=None),
    overdue_only: bool = Query(default=False),
    pagination: Paginator = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Readers see only their own borrowings.
    Librarians/Admins can filter by any user.
    """
    # Readers are restricted to their own records
    effective_user_id = user_id
    if current_user.role == UserRole.READER:
        effective_user_id = current_user.id

    filters = BorrowingFilter(
        status=status_filter,
        user_id=effective_user_id,
        book_id=book_id,
        overdue_only=overdue_only,
    )
    service = BorrowingService(db)
    items, total = await service.list_borrowings(
        filters, page=pagination.page, page_size=pagination.page_size
    )
    return make_paginated_response(
        [_borrowing_to_read(b) for b in items],
        total,
        pagination.page,
        pagination.page_size,
    )


@router.get(
    "/{borrowing_id}",
    response_model=BorrowingRead,
    summary="Get borrowing detail",
)
async def get_borrowing(
    borrowing_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    service = BorrowingService(db)
    b = await service.get_or_404(borrowing_id)

    # Readers can only view their own borrowings
    if current_user.role == UserRole.READER and b.user_id != current_user.id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Access denied.")

    return _borrowing_to_read(b)


@router.post(
    "",
    response_model=BorrowingRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_librarian)],
    summary="Issue a book to a reader (Librarian/Admin)",
)
async def issue_book(
    data: BorrowingCreate,
    db: AsyncSession = Depends(get_db),
):
    """Librarian issues a book. Enforces all business rules."""
    service = BorrowingService(db)
    b = await service.issue_book(data)
    return _borrowing_to_read(b)


@router.post(
    "/{borrowing_id}/return",
    response_model=BorrowingRead,
    dependencies=[Depends(require_librarian)],
    summary="Process book return (Librarian/Admin)",
)
async def return_book(
    borrowing_id: int,
    data: ReturnBookRequest,
    db: AsyncSession = Depends(get_db),
):
    """Processes a return, calculates overdue fine, updates available_quantity."""
    service = BorrowingService(db)
    b = await service.return_book(borrowing_id, data)
    return _borrowing_to_read(b)


@router.post(
    "/{borrowing_id}/renew",
    response_model=BorrowingRead,
    summary="Renew a borrowing",
)
async def renew_borrowing(
    borrowing_id: int,
    data: RenewBorrowingRequest,
    current_user: User = Depends(require_reader),
    db: AsyncSession = Depends(get_db),
):
    """
    Reader renews their own borrowing; Librarian/Admin can renew any.
    Enforces MAX_RENEWALS limit.
    """
    service = BorrowingService(db)
    b = await service.renew_borrowing(
        borrowing_id,
        data,
        requesting_user_id=current_user.id,
        requesting_role=current_user.role,
    )
    return _borrowing_to_read(b)


@router.post(
    "/{borrowing_id}/mark-fine-paid",
    response_model=BorrowingRead,
    dependencies=[Depends(require_librarian)],
    summary="Mark fine as paid (Librarian/Admin)",
)
async def mark_fine_paid(
    borrowing_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = BorrowingService(db)
    b = await service.mark_fine_paid(borrowing_id)
    return _borrowing_to_read(b)


@router.post(
    "/sync-overdue",
    response_model=MessageResponse,
    dependencies=[Depends(require_admin)],
    summary="Sync overdue statuses (Admin / cron trigger)",
)
async def sync_overdue(
    db: AsyncSession = Depends(get_db),
):
    """
    Batch updates all past-due borrowings to OVERDUE status and recalculates fines.
    Can be triggered manually or by a cron job.
    """
    service = BorrowingService(db)
    count = await service.sync_overdue_statuses()
    return MessageResponse(message=f"Updated {count} borrowing(s) to overdue status.")
