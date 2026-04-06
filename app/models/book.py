"""
Book model.
Tracks total stock and how many copies are currently available.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True)
    title = Column(String(256), nullable=False, index=True)
    author = Column(String(128), nullable=False, index=True)
    isbn = Column(String(20), unique=True, nullable=True, index=True)
    category = Column(String(64), nullable=True, index=True)
    description = Column(Text, nullable=True)
    total_quantity = Column(Integer, nullable=False, default=1)
    available_quantity = Column(Integer, nullable=False, default=1)
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    borrow_records = relationship(
        "BorrowRecord", back_populates="book", lazy="dynamic"
    )

    # ── Stock helpers ─────────────────────────────────────────────

    @property
    def is_available(self) -> bool:
        return self.available_quantity > 0

    def decrement_stock(self) -> None:
        """Call when a book is borrowed."""
        if self.available_quantity <= 0:
            raise ValueError(f"Book '{self.title}' is not available.")
        self.available_quantity -= 1

    def increment_stock(self) -> None:
        """Call when a book is returned."""
        if self.available_quantity >= self.total_quantity:
            raise ValueError("Available quantity cannot exceed total quantity.")
        self.available_quantity += 1

    def has_active_borrows(self, db_session) -> bool:
        """True if any copy is currently borrowed — pass the active Session."""
        from sqlalchemy import select, func
        from app.models.borrow import BorrowRecord, BorrowStatusEnum
        count = db_session.execute(
            select(func.count()).select_from(BorrowRecord).where(
                BorrowRecord.book_id == self.id,
                BorrowRecord.status == BorrowStatusEnum.BORROWED,
            )
        ).scalar_one()
        return count > 0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "category": self.category,
            "description": self.description,
            "total_quantity": self.total_quantity,
            "available_quantity": self.available_quantity,
            "is_available": self.is_available,
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self) -> str:
        return f"<Book '{self.title}' by {self.author}>"
