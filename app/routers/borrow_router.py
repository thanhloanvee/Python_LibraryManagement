"""
Borrow Router — /api/borrows/*

POST  /api/borrows                  — borrow a book       (member/admin/librarian)
PATCH /api/borrows/{id}/return      — return a book       (member/admin/librarian)
GET   /api/borrows/my               — my borrow history   (any authenticated)
GET   /api/borrows                  — all borrows         (admin/librarian)
GET   /api/borrows/{id}             — single record       (admin/librarian)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.borrow_service import BorrowService
from app.repositories.borrow_repository import BorrowRepository
from app.schemas.borrow_schema import BorrowCreateRequest
from app.dependencies.auth import any_authenticated, admin_or_librarian, all_roles
from app.models.user import User
from app.utils.pagination import pagination_meta

router = APIRouter(tags=["Borrows"])


@router.post("/", status_code=201, summary="Borrow a book")
def borrow_book(
    body: BorrowCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(all_roles),
):
    """
    Borrow a book. Subject to:
    - Maximum **5** active borrows per user
    - Book must have available copies
    """
    try:
        record = BorrowService(db).borrow_book(
            user_id=current_user.id, book_id=body.book_id
        )
        return {"success": True, "message": "Book borrowed successfully.", "data": record.to_dict()}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.patch("/{borrow_id}/return", summary="Return a borrowed book")
def return_book(
    borrow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(all_roles),
):
    """
    Return a book. A fine is automatically calculated if overdue.
    Fine = overdue_days × $1.00/day (configurable via `FINE_PER_DAY`).
    """
    try:
        record = BorrowService(db).return_book(
            borrow_id=borrow_id, user_id=current_user.id
        )
        return {"success": True, "message": "Book returned successfully.", "data": record.to_dict()}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/my", summary="My borrow history")
def my_borrows(
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(any_authenticated),
):
    result = BorrowService(db).get_user_borrows(
        current_user.id, page=page, per_page=per_page
    )
    items = [r.to_dict() for r in result["items"]]
    return {"success": True, "data": items, "meta": pagination_meta(result)}


@router.get("/", summary="List all borrows (admin/librarian)")
def all_borrows(
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(get_db),
    _=Depends(admin_or_librarian),
):
    result = BorrowService(db).get_all_borrows(page=page, per_page=per_page)
    items = [r.to_dict() for r in result["items"]]
    return {"success": True, "data": items, "meta": pagination_meta(result)}


@router.get("/{borrow_id}", summary="Get single borrow record (admin/librarian)")
def get_borrow(
    borrow_id: int,
    db: Session = Depends(get_db),
    _=Depends(admin_or_librarian),
):
    record = BorrowRepository(db).get_by_id(borrow_id)
    if not record:
        raise HTTPException(status_code=404, detail="Borrow record not found.")
    return {"success": True, "data": record.to_dict()}
