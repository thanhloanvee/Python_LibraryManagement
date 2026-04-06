"""
Book Router — /api/books/*

GET    /api/books              — search/list books  (any authenticated)
GET    /api/books/{id}         — book detail        (any authenticated)
POST   /api/books              — add book           (admin, librarian)
PUT    /api/books/{id}         — update book        (admin, librarian)
DELETE /api/books/{id}         — delete book        (admin)
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.book_service import BookService
from app.schemas.book_schema import BookCreateRequest, BookUpdateRequest
from app.dependencies.auth import any_authenticated, admin_or_librarian, admin_only
from app.utils.pagination import pagination_meta

router = APIRouter(tags=["Books"])


@router.get("/", summary="Search / list books")
def list_books(
    q: str = Query(default="", description="Search by title or author"),
    category: str = Query(default=None, description="Filter by category"),
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(get_db),
    _=Depends(any_authenticated),
):
    result = BookService(db).search_books(query=q, category=category, page=page, per_page=per_page)
    items = [b.to_dict() for b in result["items"]]
    return {"success": True, "data": items, "meta": pagination_meta(result)}


@router.get("/{book_id}", summary="Get book by ID")
def get_book(book_id: int, db: Session = Depends(get_db), _=Depends(any_authenticated)):
    try:
        return {"success": True, "data": BookService(db).get_book(book_id).to_dict()}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/", status_code=201, summary="Add a new book (admin/librarian)")
def add_book(
    body: BookCreateRequest,
    db: Session = Depends(get_db),
    _=Depends(admin_or_librarian),
):
    try:
        book = BookService(db).add_book(**body.model_dump())
        return {"success": True, "message": "Book added.", "data": book.to_dict()}
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.put("/{book_id}", summary="Update a book (admin/librarian)")
def update_book(
    book_id: int,
    body: BookUpdateRequest,
    db: Session = Depends(get_db),
    _=Depends(admin_or_librarian),
):
    try:
        # Only pass fields that were explicitly set
        data = body.model_dump(exclude_unset=True)
        book = BookService(db).update_book(book_id, **data)
        return {"success": True, "message": "Book updated.", "data": book.to_dict()}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete("/{book_id}", summary="Delete a book (admin)")
def delete_book(book_id: int, db: Session = Depends(get_db), _=Depends(admin_only)):
    try:
        BookService(db).delete_book(book_id)
        return {"success": True, "message": "Book deleted."}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
