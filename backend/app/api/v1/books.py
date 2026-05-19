"""
Books router.

RBAC:
  - GET  /books          → Public
  - GET  /books/{id}     → Public
  - POST /books          → Librarian or Admin
  - PATCH /books/{id}    → Librarian or Admin
  - DELETE /books/{id}   → Admin only
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.rbac import require_admin, require_librarian
from app.models.book import BookLanguage, BookStatus
from app.schemas.book import BookCreate, BookFilter, BookRead, BookUpdate
from app.schemas.common import MessageResponse, PaginatedResponse
from app.services.book import BookService
from app.utils.pagination import Paginator, make_paginated_response

router = APIRouter(prefix="/books", tags=["Books"])


@router.get(
    "",
    response_model=PaginatedResponse[BookRead],
    summary="List books with optional filters",
)
async def list_books(
    title: Optional[str] = Query(default=None),
    author: Optional[str] = Query(default=None),
    isbn: Optional[str] = Query(default=None),
    category_id: Optional[int] = Query(default=None),
    status: Optional[BookStatus] = Query(default=None),
    language: Optional[BookLanguage] = Query(default=None),
    search: Optional[str] = Query(
        default=None, description="Full-text search across title, author, ISBN"
    ),
    pagination: Paginator = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """Public book listing with filtering and pagination."""
    filters = BookFilter(
        title=title,
        author=author,
        isbn=isbn,
        category_id=category_id,
        status=status,
        language=language,
        search=search,
    )
    service = BookService(db)
    items, total = await service.list_books(
        filters, page=pagination.page, page_size=pagination.page_size
    )
    return make_paginated_response(
        [BookRead.model_validate(b) for b in items],
        total,
        pagination.page,
        pagination.page_size,
    )


@router.get(
    "/{book_id}",
    response_model=BookRead,
    summary="Get a book by ID",
)
async def get_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = BookService(db)
    return await service.get_or_404(book_id)


@router.post(
    "",
    response_model=BookRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_librarian)],
    summary="Create a book (Librarian/Admin)",
)
async def create_book(
    data: BookCreate,
    db: AsyncSession = Depends(get_db),
):
    service = BookService(db)
    return await service.create_book(data)


@router.patch(
    "/{book_id}",
    response_model=BookRead,
    dependencies=[Depends(require_librarian)],
    summary="Update a book (Librarian/Admin)",
)
async def update_book(
    book_id: int,
    data: BookUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = BookService(db)
    return await service.update_book(book_id, data)


@router.delete(
    "/{book_id}",
    response_model=MessageResponse,
    dependencies=[Depends(require_admin)],
    summary="Delete a book (Admin)",
)
async def delete_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Deletes a book only if no active borrowings exist."""
    service = BookService(db)
    await service.delete_book(book_id)
    return MessageResponse(message="Book deleted successfully.")
