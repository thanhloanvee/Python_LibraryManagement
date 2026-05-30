"""Book service — business logic for book management."""
from __future__ import annotations

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
                    detail="This ISBN already exists.",
                )
        # Validate category exists
        if data.category_id is not None:
            cat = await self._cat_repo.get_by_id(data.category_id)
            if not cat:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Category not found.",
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
                        detail="This ISBN already exists.",
                    )

        # Validate category if being updated
        if "category_id" in update_data and update_data["category_id"] is not None:
            cat = await self._cat_repo.get_by_id(update_data["category_id"])
            if not cat:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Category not found.",
                )

        # Cross-field validation: available_quantity <= quantity
        new_qty = update_data.get("quantity", book.quantity)
        new_avail = update_data.get("available_quantity", book.available_quantity)
        if new_avail > new_qty:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="available_quantity cannot exceed total quantity.",
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
                detail="Cannot delete this book because it has active borrowings.",
            )
        await self._repo.delete(book)
