"""Public site routes: home, book browsing/detail."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.book import Book, BookStatus
from app.models.category import Category
from app.schemas.book import BookFilter
from app.schemas.review import ReviewCreate
from app.services.book import BookService
from app.services.category import CategoryService
from app.services.review import ReviewService
from app.web.dependencies import get_optional_web_user, require_reader
from app.web.templating import render, set_flash

router = APIRouter(tags=["Web Site"])


@router.get("/")
async def home(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_optional_web_user),
):
    """Home page."""
    total_books = (await db.execute(select(func.count(Book.id)))).scalar_one()
    available_books = (
        await db.execute(
            select(func.count(Book.id)).where(
                Book.status == BookStatus.AVAILABLE,
                Book.available_quantity > 0,
            )
        )
    ).scalar_one()
    total_categories = (
        await db.execute(select(func.count(Category.id)))
    ).scalar_one()

    # Featured books — latest 6
    featured, _ = await BookService(db).list_books(
        BookFilter(status=BookStatus.AVAILABLE), page=1, page_size=6
    )
    return render(
        "site/index.html",
        {
            "total_books": total_books,
            "available_books": available_books,
            "total_categories": total_categories,
            "featured_books": featured,
        },
        request,
    )


@router.get("/books")
async def books_list(
    request: Request,
    search: str = "",
    category_id: str | None = None,
    language: str | None = None,
    page: int = 1,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_optional_web_user),
):
    """Public book browsing."""
    from app.models.book import BookLanguage

    cat_id: int | None = int(category_id) if category_id else None
    filters = BookFilter(
        search=search or None,
        category_id=cat_id,
        language=BookLanguage(language) if language else None,
    )
    books, total = await BookService(db).list_books(filters, page=page, page_size=12)
    categories, _ = await CategoryService(db).list_categories()

    ctx = {
        "books": books,
        "total": total,
        "page": page,
        "page_size": 12,
        "categories": categories,
        "filters": {
            "search": search,
            "category_id": cat_id,
            "language": language,
        },
    }

    # HTMX partial refresh — return only the book grid + pagination
    if request.headers.get("HX-Request"):
        return render("partials/book_grid.html", ctx, request)
    return render("books/index.html", ctx, request)


@router.post("/books/{book_id}/review")
async def submit_review(
    book_id: int,
    request: Request,
    rating: int = Form(...),
    comment: str = Form(""),
    db: AsyncSession = Depends(get_db),
    user=Depends(require_reader),
):
    """Handle review form submission from the book detail page."""
    try:
        data = ReviewCreate(book_id=book_id, rating=rating, comment=comment or None)
        await ReviewService(db).create_review(data, user.id)
        response = RedirectResponse(url=f"/books/{book_id}", status_code=303)
        set_flash(response, "Đánh giá đã được gửi thành công!", "success")
    except HTTPException as exc:
        response = RedirectResponse(url=f"/books/{book_id}", status_code=303)
        set_flash(response, exc.detail, "error")
    return response


@router.get("/books/{book_id}")
async def book_detail(
    book_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_optional_web_user),
):
    """Book detail page."""
    book = await BookService(db).get_or_404(book_id)
    reviews, _ = await ReviewService(db).list_reviews(
        book_id=book_id, page=1, page_size=20
    )
    avg_rating = await ReviewService(db).get_average_rating(book_id)

    # Check if current user can review / has active borrowing
    can_review = False
    already_reviewed = False
    has_active_borrow = False
    if user:
        from app.repositories.review import ReviewRepository
        from app.repositories.borrowing import BorrowingRepository
        can_review = await ReviewRepository(db).user_has_borrowed_book(user.id, book_id)
        already_reviewed = (
            await ReviewRepository(db).get_by_user_and_book(user.id, book_id)
        ) is not None
        from app.models.borrowing import BorrowingStatus
        active = await BorrowingRepository(db).get_active_for_user_book(user.id, book_id)
        has_active_borrow = active is not None

    return render(
        "books/detail.html",
        {
            "book": book,
            "reviews": reviews,
            "avg_rating": avg_rating,
            "can_review": can_review,
            "already_reviewed": already_reviewed,
            "has_active_borrow": has_active_borrow,
        },
        request,
    )
