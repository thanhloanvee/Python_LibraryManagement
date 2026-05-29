"""Admin book management."""
from __future__ import annotations

import os
import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.book import BookLanguage, BookStatus
from app.schemas.book import BookCreate, BookFilter, BookUpdate
from app.services.book import BookService
from app.services.category import CategoryService
from app.web.dependencies import require_admin, require_librarian
from app.web.templating import render, set_flash

router = APIRouter()

UPLOAD_DIR = Path(__file__).resolve().parents[2] / "static" / "uploads"


def _form_to_book_dict(
    title: str, author: str, isbn: str, publisher: str,
    publication_year: int, language: str, description: str,
    quantity: int, status: str, category_id: int | None,
    cover_file: UploadFile | None,
    existing_cover: str | None = None,
) -> dict:
    cover_image = existing_cover
    if cover_file and cover_file.filename:
        ext = Path(cover_file.filename).suffix.lower()
        safe_name = f"{isbn.replace('/', '_')}{ext}"
        dest = UPLOAD_DIR / safe_name
        with open(dest, "wb") as f:
            shutil.copyfileobj(cover_file.file, f)
        cover_image = f"static/uploads/{safe_name}"

    return {
        "title": title,
        "author": author,
        "isbn": isbn,
        "publisher": publisher,
        "publication_year": publication_year,
        "language": BookLanguage(language),
        "description": description or None,
        "quantity": quantity,
        "status": BookStatus(status),
        "category_id": category_id or None,
        "cover_image": cover_image,
    }


@router.get("/admin/books")
async def books_index(
    request: Request,
    search: str = "",
    category_id: str | None = None,
    status: str | None = None,
    page: int = 1,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_librarian),
):
    cat_id = int(category_id) if category_id else None
    filters = BookFilter(
        search=search or None,
        category_id=cat_id,
        status=BookStatus(status) if status else None,
    )
    books, total = await BookService(db).list_books(filters, page=page, page_size=20)
    categories, _ = await CategoryService(db).list_categories()

    ctx = {
        "books": books,
        "total": total,
        "page": page,
        "page_size": 20,
        "categories": categories,
        "filters": {"search": search, "category_id": cat_id, "status": status},
    }
    if request.headers.get("HX-Request"):
        return render("admin/books/_rows.html", ctx, request)
    return render("admin/books/index.html", ctx, request)


@router.get("/admin/books/new")
async def book_new_form(
    request: Request,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    categories, _ = await CategoryService(db).list_categories()
    return render(
        "admin/books/form.html",
        {
            "book": None,
            "categories": categories,
            "languages": list(BookLanguage),
            "statuses": list(BookStatus),
        },
        request,
    )


@router.post("/admin/books/new")
async def book_create(
    request: Request,
    title: str = Form(...),
    author: str = Form(...),
    isbn: str = Form(...),
    publisher: str = Form(...),
    publication_year: int = Form(...),
    language: str = Form(...),
    description: str = Form(default=""),
    quantity: int = Form(...),
    status: str = Form(...),
    category_id: int | None = Form(default=None),
    cover_file: UploadFile | None = File(default=None),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    try:
        data = _form_to_book_dict(
            title, author, isbn, publisher, publication_year,
            language, description, quantity, status, category_id, cover_file,
        )
        data["available_quantity"] = quantity  # set only on create
        await BookService(db).create_book(BookCreate(**data))
        resp = RedirectResponse(url="/admin/books", status_code=302)
        set_flash(resp, f"Sách '{title}' đã được tạo thành công.", "success")
        return resp
    except Exception as exc:
        categories, _ = await CategoryService(db).list_categories()
        return render(
            "admin/books/form.html",
            {
                "book": None,
                "categories": categories,
                "languages": list(BookLanguage),
                "statuses": list(BookStatus),
                "error": str(exc.detail if hasattr(exc, "detail") else exc),
                "form": request,
            },
            request,
        )


@router.get("/admin/books/{book_id}/edit")
async def book_edit_form(
    book_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    book = await BookService(db).get_or_404(book_id)
    categories, _ = await CategoryService(db).list_categories()
    return render(
        "admin/books/form.html",
        {
            "book": book,
            "categories": categories,
            "languages": list(BookLanguage),
            "statuses": list(BookStatus),
        },
        request,
    )


@router.post("/admin/books/{book_id}/edit")
async def book_update(
    book_id: int,
    request: Request,
    title: str = Form(...),
    author: str = Form(...),
    isbn: str = Form(...),
    publisher: str = Form(...),
    publication_year: int = Form(...),
    language: str = Form(...),
    description: str = Form(default=""),
    quantity: int = Form(...),
    status: str = Form(...),
    category_id: int | None = Form(default=None),
    cover_file: UploadFile | None = File(default=None),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    try:
        svc = BookService(db)
        book = await svc.get_or_404(book_id)
        data = _form_to_book_dict(
            title, author, isbn, publisher, publication_year,
            language, description, quantity, status, category_id, cover_file,
            existing_cover=book.cover_image,
        )
        await svc.update_book(book_id, BookUpdate(**data))
        resp = RedirectResponse(url="/admin/books", status_code=302)
        set_flash(resp, f"Sách '{title}' đã được cập nhật.", "success")
        return resp
    except Exception as exc:
        book = await BookService(db).get_or_404(book_id)
        categories, _ = await CategoryService(db).list_categories()
        return render(
            "admin/books/form.html",
            {
                "book": book,
                "categories": categories,
                "languages": list(BookLanguage),
                "statuses": list(BookStatus),
                "error": str(exc.detail if hasattr(exc, "detail") else exc),
            },
            request,
        )


@router.post("/admin/books/{book_id}/delete")
async def book_delete(
    book_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    try:
        book = await BookService(db).get_or_404(book_id)
        title = book.title
        await BookService(db).delete_book(book_id)
        resp = RedirectResponse(url="/admin/books", status_code=302)
        set_flash(resp, f"Sách '{title}' đã được xóa.", "success")
        return resp
    except Exception as exc:
        resp = RedirectResponse(url="/admin/books", status_code=302)
        set_flash(resp, str(exc.detail if hasattr(exc, "detail") else exc), "error")
        return resp
