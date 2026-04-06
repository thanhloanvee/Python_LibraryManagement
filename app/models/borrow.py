"""
BorrowRecord and Fine models.

BorrowRecord lifecycle:
  BORROWED  →  RETURNED   (on-time return, no fine)
  BORROWED  →  OVERDUE    (due_date passed, fine calculated on return)
"""

import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, DateTime, Enum, ForeignKey, Numeric, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class BorrowStatusEnum(str, enum.Enum):
    BORROWED = "borrowed"
    RETURNED = "returned"
    OVERDUE = "overdue"


class BorrowRecord(Base):
    __tablename__ = "borrow_records"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    book_id = Column(
        Integer, ForeignKey("books.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    borrow_date = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    due_date = Column(DateTime, nullable=False)
    return_date = Column(DateTime, nullable=True)
    status = Column(
        Enum(BorrowStatusEnum),
        nullable=False,
        default=BorrowStatusEnum.BORROWED,
    )

    # Relationships
    user = relationship("User", back_populates="borrow_records")
    book = relationship("Book", back_populates="borrow_records")
    fine = relationship(
        "Fine", back_populates="borrow_record", uselist=False, cascade="all, delete-orphan"
    )

    # ── Helpers ───────────────────────────────────────────────────

    def is_overdue(self) -> bool:
        """True when borrow is still active and past due date."""
        if self.status != BorrowStatusEnum.BORROWED:
            return False
        return datetime.now(timezone.utc) > self.due_date.replace(tzinfo=timezone.utc)

    def overdue_days(self) -> int:
        """Number of days overdue (only valid while status == BORROWED). Returns 0 if not overdue."""
        if not self.is_overdue():
            return 0
        delta = datetime.now(timezone.utc) - self.due_date.replace(tzinfo=timezone.utc)
        return max(0, delta.days)

    def overdue_days_at_return(self, now: datetime) -> int:
        """Days overdue at a given moment, regardless of current status. Returns 0 if not late."""
        delta = now - self.due_date.replace(tzinfo=timezone.utc)
        return max(0, delta.days)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "book_id": self.book_id,
            "book_title": self.book.title if self.book else None,
            "borrow_date": self.borrow_date.isoformat(),
            "due_date": self.due_date.isoformat(),
            "return_date": self.return_date.isoformat() if self.return_date else None,
            "status": self.status.value,
            "fine": self.fine.to_dict() if self.fine else None,
        }

    def __repr__(self) -> str:
        return f"<BorrowRecord user={self.user_id} book={self.book_id} status={self.status.value}>"


class Fine(Base):
    __tablename__ = "fines"

    id = Column(Integer, primary_key=True)
    borrow_id = Column(
        Integer,
        ForeignKey("borrow_records.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,      # one fine per borrow
        index=True,
    )
    overdue_days = Column(Integer, nullable=False, default=0)
    amount = Column(Numeric(10, 2), nullable=False, default=0.00)
    is_paid = Column(Boolean, nullable=False, default=False)
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    borrow_record = relationship("BorrowRecord", back_populates="fine")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "borrow_id": self.borrow_id,
            "overdue_days": self.overdue_days,
            "amount": float(self.amount),
            "is_paid": self.is_paid,
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self) -> str:
        return f"<Fine borrow={self.borrow_id} amount={self.amount} paid={self.is_paid}>"
