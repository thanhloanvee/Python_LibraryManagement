"""
Import all models here so that:
1. Alembic env.py can import this package and discover all tables.
2. Back-references resolve correctly when SQLAlchemy builds the mapper.
"""
from app.models.user import User, UserRole, UserStatus
from app.models.category import Category
from app.models.book import Book, BookStatus, BookLanguage
from app.models.borrowing import Borrowing, BorrowingStatus, BookCondition
from app.models.review import Review, ReviewStatus

__all__ = [
    "User",
    "UserRole",
    "UserStatus",
    "Category",
    "Book",
    "BookStatus",
    "BookLanguage",
    "Borrowing",
    "BorrowingStatus",
    "BookCondition",
    "Review",
    "ReviewStatus",
]
