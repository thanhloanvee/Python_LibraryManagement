"""Book service — business logic for book management."""
from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.book import Book
from app.repositories.book import BookRepository
from app.repositories.category import CategoryRepository
from app.schemas.book import BookCreate, BookFilter, BookUpdate
from app.services.base import BaseService


class BookService(BaseService):
    def __init__(self, db: AsyncSession) -> None:
        self._repo = BookRepository(db)
        self._cat_repo = CategoryRepository(db)

    async def get_or_404(self, book_id: int) -> Book:
        book = await self._repo.get_by_id(book_id)
        return await super().get_or_404(book, "Book")

    async def list_books(
        self,
        filters: BookFilter,
        *,
        page: int = 1,
        page_size: int = 20,
    ):
        offset = self.calculate_offset(page, page_size)
        return await self._repo.list_books(
            title=filters.title,
            author=filters.author,
            isbn=filters.isbn,
            category_id=filters.category_id,
            status=filters.status,
            language=filters.language,
            search=filters.search,
            offset=offset,
            limit=page_size,
        )

    async def create_book(self, data: BookCreate) -> Book:
        # ISBN uniqueness check
        if data.isbn:
            existing = await self._repo.get_by_isbn(data.isbn)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="ISBN này đã tồn tại.",
                )
        # Validate category exists
        if data.category_id is not None:
            cat = await self._cat_repo.get_by_id(data.category_id)
            if not cat:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Danh mục không tồn tại.",
                )
        book = Book(**data.model_dump())
        return await self._repo.create(book)

    async def update_book(self, book_id: int, data: BookUpdate) -> Book:
        book = await self.get_or_404(book_id)

        update_data = data.model_dump(exclude_unset=True)

        # ISBN uniqueness check only when ISBN is being changed
        if "isbn" in update_data and update_data["isbn"] != book.isbn:
            if update_data["isbn"] is not None:
                existing = await self._repo.get_by_isbn(update_data["isbn"])
                if existing and existing.id != book.id:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail="ISBN này đã tồn tại.",
                    )

        # Validate category if being updated
        if "category_id" in update_data and update_data["category_id"] is not None:
            cat = await self._cat_repo.get_by_id(update_data["category_id"])
            if not cat:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Danh mục không tồn tại.",
                )

        # Handle quantity/available_quantity changes
        borrowed_count = book.quantity - book.available_quantity

        if "available_quantity" in update_data and "quantity" not in update_data:
            # When available_quantity is edited, update total quantity
            # New total = new available + borrowed copies (still out on loan)
            new_avail = update_data["available_quantity"]
            update_data["quantity"] = new_avail + borrowed_count
        elif "quantity" in update_data and "available_quantity" not in update_data:
            # When quantity is edited (create), auto-set available_quantity
            new_qty = update_data["quantity"]
            qty_diff = new_qty - book.quantity if book.id else 0

            if qty_diff > 0:
                # If quantity increased, increase available_quantity by the same amount
                update_data["available_quantity"] = book.available_quantity + qty_diff
            elif qty_diff < 0:
                # If quantity decreased, adjust available proportionally
                new_avail = max(new_qty - borrowed_count, 0)
                update_data["available_quantity"] = new_avail

        # Cross-field validation: available_quantity <= quantity
        new_qty = update_data.get("quantity", book.quantity)
        new_avail = update_data.get("available_quantity", book.available_quantity)
        if new_avail > new_qty:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Số lượng khả dụng không được vượt quá tổng số lượng.",
            )

        for key, value in update_data.items():
            setattr(book, key, value)

        return await self._repo.save(book)

    async def delete_book(self, book_id: int) -> None:
        """Delete a book only if it has no active borrowings."""
        book = await self.get_or_404(book_id)
        if await self._repo.has_active_borrowings(book_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Không thể xóa sách này vì còn phiếu mượn chưa hoàn thành.",
            )
        await self._repo.delete(book)
