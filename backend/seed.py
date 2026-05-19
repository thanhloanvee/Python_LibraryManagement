"""
Database seed script.

Run:
    cd backend
    python seed.py

Creates:
  - Admin, Librarian, and sample Reader accounts
  - Sample categories
  - Sample books (Vietnamese and English)
"""
from __future__ import annotations

import asyncio
import sys
from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

sys.path.insert(0, ".")

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.base import Base
import app.models  # noqa: F401 — register all models
from app.models.book import Book, BookLanguage, BookStatus
from app.models.borrowing import Borrowing, BorrowingStatus
from app.models.category import Category
from app.models.review import Review, ReviewStatus
from app.models.user import User, UserRole, UserStatus

settings = get_settings()


async def seed(session: AsyncSession) -> None:
    print("Seeding database…")

    # Users
    admin = User(
        username=settings.admin_username,
        email=settings.admin_email,
        password_hash=hash_password(settings.admin_password),
        full_name=settings.admin_full_name,
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
    )
    librarian = User(
        username="librarian1",
        email="librarian@library.local",
        password_hash=hash_password("Lib@123456"),
        full_name="Nguyễn Thị Thủ Thư",
        role=UserRole.LIBRARIAN,
        status=UserStatus.ACTIVE,
    )
    reader1 = User(
        username="reader1",
        email="reader1@example.com",
        password_hash=hash_password("Reader@123"),
        full_name="Trần Văn Đọc",
        phone="0901234567",
        role=UserRole.READER,
        status=UserStatus.ACTIVE,
    )
    reader2 = User(
        username="reader2",
        email="reader2@example.com",
        password_hash=hash_password("Reader@123"),
        full_name="Lê Thị Mượn",
        phone="0912345678",
        role=UserRole.READER,
        status=UserStatus.ACTIVE,
    )
    session.add_all([admin, librarian, reader1, reader2])
    await session.flush()
    print(f"  Created users: {admin.username}, {librarian.username}, "
          f"{reader1.username}, {reader2.username}")

    # Categories
    categories = [
        Category(name="Văn học Việt Nam", description="Tác phẩm văn học Việt Nam"),
        Category(name="Khoa học & Công nghệ", description="Sách khoa học và kỹ thuật"),
        Category(name="Lịch sử", description="Lịch sử Việt Nam và thế giới"),
        Category(name="Kinh tế", description="Kinh tế, quản trị, tài chính"),
        Category(name="Ngoại ngữ", description="Sách học ngoại ngữ"),
        Category(name="Thiếu nhi", description="Sách dành cho trẻ em"),
        Category(name="Computer Science", description="Programming and software engineering"),
    ]
    session.add_all(categories)
    await session.flush()
    print(f"  Created {len(categories)} categories.")

    # Category map for convenience
    cat = {c.name: c for c in categories}

    # Books
    books = [
        Book(
            title="Dế Mèn Phiêu Lưu Ký",
            author="Tô Hoài",
            isbn="978-604-2-10001-1",
            publisher="NXB Kim Đồng",
            publication_year=1941,
            language=BookLanguage.VIETNAMESE,
            description="Truyện dài nổi tiếng về Dế Mèn.",
            quantity=5,
            available_quantity=5,
            status=BookStatus.AVAILABLE,
            category_id=cat["Thiếu nhi"].id,
        ),
        Book(
            title="Số Đỏ",
            author="Vũ Trọng Phụng",
            isbn="978-604-2-10002-2",
            publisher="NXB Văn học",
            publication_year=1936,
            language=BookLanguage.VIETNAMESE,
            description="Tiểu thuyết trào phúng kinh điển.",
            quantity=3,
            available_quantity=3,
            status=BookStatus.AVAILABLE,
            category_id=cat["Văn học Việt Nam"].id,
        ),
        Book(
            title="Lập Trình Python Cơ Bản",
            author="Nguyễn Văn Lập",
            isbn="978-604-2-20001-3",
            publisher="NXB Thông tin & Truyền thông",
            publication_year=2022,
            language=BookLanguage.VIETNAMESE,
            description="Giáo trình Python dành cho người mới bắt đầu.",
            quantity=10,
            available_quantity=10,
            status=BookStatus.AVAILABLE,
            category_id=cat["Khoa học & Công nghệ"].id,
        ),
        Book(
            title="Clean Code",
            author="Robert C. Martin",
            isbn="978-0-13-235088-4",
            publisher="Prentice Hall",
            publication_year=2008,
            language=BookLanguage.ENGLISH,
            description="A handbook of agile software craftsmanship.",
            quantity=4,
            available_quantity=4,
            status=BookStatus.AVAILABLE,
            category_id=cat["Computer Science"].id,
        ),
        Book(
            title="The Pragmatic Programmer",
            author="David Thomas, Andrew Hunt",
            isbn="978-0-13-595705-9",
            publisher="Addison-Wesley",
            publication_year=2019,
            language=BookLanguage.ENGLISH,
            description="Your journey to mastery.",
            quantity=3,
            available_quantity=3,
            status=BookStatus.AVAILABLE,
            category_id=cat["Computer Science"].id,
        ),
        Book(
            title="Lịch Sử Việt Nam",
            author="Nhiều tác giả",
            isbn="978-604-2-30001-5",
            publisher="NXB Giáo dục",
            publication_year=2019,
            language=BookLanguage.VIETNAMESE,
            description="Bộ sách lịch sử Việt Nam từ thời dựng nước.",
            quantity=6,
            available_quantity=6,
            status=BookStatus.AVAILABLE,
            category_id=cat["Lịch sử"].id,
        ),
    ]
    session.add_all(books)
    await session.flush()
    print(f"  Created {len(books)} books.")

    # Sample borrowings
    today = date.today()
    b1 = Borrowing(
        user_id=reader1.id,
        book_id=books[0].id,
        borrow_date=today - timedelta(days=5),
        due_date=today + timedelta(days=9),
        status=BorrowingStatus.BORROWED,
    )
    # Overdue borrowing to demo fine calculation
    b2 = Borrowing(
        user_id=reader2.id,
        book_id=books[3].id,
        borrow_date=today - timedelta(days=20),
        due_date=today - timedelta(days=6),
        status=BorrowingStatus.OVERDUE,
        fine_amount=6 * settings.fine_per_day,
    )
    # Returned borrowing (reader1 returned book[3] to allow reviewing)
    b3 = Borrowing(
        user_id=reader1.id,
        book_id=books[3].id,
        borrow_date=today - timedelta(days=30),
        due_date=today - timedelta(days=16),
        return_date=today - timedelta(days=17),
        status=BorrowingStatus.RETURNED,
        fine_amount=0.0,
    )
    books[0].available_quantity -= 1
    books[3].available_quantity -= 1

    session.add_all([b1, b2, b3])
    await session.flush()
    print("  Created 3 sample borrowings.")

    # Sample review (reader1 has borrowed books[3], so can review it)
    review = Review(
        book_id=books[3].id,
        user_id=reader1.id,
        rating=5,
        comment="Excellent book on software craftsmanship!",
        status=ReviewStatus.ACTIVE,
    )
    session.add(review)
    await session.flush()
    print("  Created 1 sample review.")

    await session.commit()
    print("Seed complete!")


async def main() -> None:
    engine = create_async_engine(
        settings.database_url,
        echo=False,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    SessionLocal = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )
    async with SessionLocal() as session:
        await seed(session)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
