"""
BookService — book CRUD and search.

Business rules enforced:
  - ISBN uniqueness (if provided)
  - Cannot delete a book that is currently borrowed
  - available_quantity <= total_quantity at all times
"""

import logging
from sqlalchemy.orm import Session

from app.models.book import Book
from app.repositories.book_repository import BookRepository

logger = logging.getLogger(__name__)


class BookService:

    def __init__(self, db: Session) -> None:
        self._book_repo = BookRepository(db)
        self._db = db

    def add_book(self, **kwargs) -> Book:
        isbn = kwargs.get("isbn")
        if isbn and self._book_repo.get_by_isbn(isbn):
            raise ValueError(f"A book with ISBN '{isbn}' already exists.")
        total_qty = kwargs.get("total_quantity", 1)
        book = Book(
            title=kwargs["title"],
            author=kwargs["author"],
            isbn=isbn,
            category=kwargs.get("category"),
            description=kwargs.get("description"),
            total_quantity=total_qty,
            available_quantity=total_qty,
        )
        self._book_repo.add(book)
        self._book_repo.commit()
        logger.info("Book added: '%s' by %s", book.title, book.author)
        return book

    def get_book(self, book_id: int) -> Book:
        book = self._book_repo.get_by_id(book_id)
        if not book:
            raise ValueError(f"Book with id={book_id} not found.")
        return book

    def search_books(self, query: str = "", category: str = None, page: int = 1, per_page: int = 20) -> dict:
        return self._book_repo.search(query=query, category=category, page=page, per_page=per_page)

    def update_book(self, book_id: int, **kwargs) -> Book:
        book = self.get_book(book_id)
        new_isbn = kwargs.get("isbn")
        if new_isbn and new_isbn != book.isbn:
            if self._book_repo.get_by_isbn(new_isbn):
                raise ValueError(f"ISBN '{new_isbn}' is already used by another book.")
        new_total = kwargs.get("total_quantity")
        if new_total is not None:
            diff = new_total - book.total_quantity
            new_available = book.available_quantity + diff
            if new_available < 0:
                raise ValueError(
                    "Cannot reduce total_quantity below the number of currently borrowed copies."
                )
            book.available_quantity = new_available
            book.total_quantity = new_total
        for field in ("title", "author", "isbn", "category", "description"):
            if field in kwargs and kwargs[field] is not None:
                setattr(book, field, kwargs[field])
        self._book_repo.commit()
        logger.info("Book updated: id=%d '%s'", book.id, book.title)
        return book

    def delete_book(self, book_id: int) -> None:
        book = self.get_book(book_id)
        if book.has_active_borrows(self._db):
            raise ValueError(
                f"Cannot delete '{book.title}': one or more copies are currently borrowed."
            )
        self._book_repo.delete(book)
        self._book_repo.commit()
        logger.info("Book deleted: id=%d '%s'", book_id, book.title)
