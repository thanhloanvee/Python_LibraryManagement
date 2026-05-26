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
from datetime import date, timedelta, datetime, timezone

from sqlalchemy import select
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

    # Skip if already seeded
    existing_admin = await session.scalar(
        select(User).where(User.username == settings.admin_username)
    )
    if existing_admin:
        print("Database already seeded. Skipping.")
        return

    # ------------------------------------------------------------------
    # USERS
    # ------------------------------------------------------------------
    pw_reader = hash_password("Reader@123")

    admin = User(
        username=settings.admin_username,
        email=settings.admin_email,
        password_hash=hash_password(settings.admin_password),
        full_name=settings.admin_full_name,
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
        created_at=datetime.now(timezone.utc) - timedelta(days=730),
    )
    lib1 = User(
        username="librarian1",
        email="librarian1@library.local",
        password_hash=hash_password("Lib@123456"),
        full_name="Nguyễn Thị Thủ Thư",
        phone="0241000001",
        role=UserRole.LIBRARIAN,
        status=UserStatus.ACTIVE,
        created_at=datetime.now(timezone.utc) - timedelta(days=400),
    )
    lib2 = User(
        username="librarian2",
        email="librarian2@library.local",
        password_hash=hash_password("Lib@123456"),
        full_name="Phạm Văn Quản Lý",
        phone="0241000002",
        role=UserRole.LIBRARIAN,
        status=UserStatus.ACTIVE,
        created_at=datetime.now(timezone.utc) - timedelta(days=350),
    )

    readers_data = [
        # (username, email, full_name, phone, address, active, joined_days_ago)
        # joined_days_ago chosen to be before the earliest borrowing for that user
        ("tranvandoc",    "tranvandoc@gmail.com",    "Trần Văn Đọc",       "0901234567", "12 Lý Thường Kiệt, Hà Nội",        True,  70),
        ("lethimuon",     "lethimuon@gmail.com",     "Lê Thị Mượn",        "0912345678", "45 Trần Hưng Đạo, TP.HCM",         True,  55),
        ("nguyenvanan",   "nguyenvanan@gmail.com",   "Nguyễn Văn An",      "0923456789", "78 Nguyễn Huệ, Đà Nẵng",           True,  50),
        ("phamthibinh",   "phamthibinh@gmail.com",   "Phạm Thị Bình",      "0934567890", "22 Hoàng Diệu, Huế",               True,  45),
        ("hoangvancuong", "hoangvancuong@gmail.com", "Hoàng Văn Cường",    "0945678901", "5 Phan Bội Châu, Hải Phòng",       True,  60),
        ("vuthidung",     "vuthidung@gmail.com",     "Vũ Thị Dung",        "0956789012", "99 Ngô Quyền, Hà Nội",             True,  65),
        ("dangvanem",     "dangvanem@gmail.com",     "Đặng Văn Em",        "0967890123", "3 Lê Lợi, Cần Thơ",               True,  52),
        ("buithiphuong",  "buithiphuong@gmail.com",  "Bùi Thị Phương",     "0978901234", "14 Đinh Tiên Hoàng, Nha Trang",    True,  46),
        ("dotronggiang",  "dotronggiang@gmail.com",  "Đỗ Trọng Giang",     "0989012345", "7 Pasteur, Biên Hòa",              True,  58),
        ("trinhthihai",   "trinhthihai@gmail.com",   "Trịnh Thị Hải",      "0990123456", "31 Nguyễn Trãi, Vũng Tàu",        True,  40),
        ("lyvanich",      "lyvanich@gmail.com",      "Lý Văn Ich",         "0901230001", "55 Hai Bà Trưng, Hà Nội",         True,  70),
        ("maithibich",    "maithibich@gmail.com",    "Mai Thị Bích",        "0912340002", "18 Nguyễn Đình Chiểu, TP.HCM",    True,  80),
        ("tranvankhai",   "tranvankhai@gmail.com",   "Trần Văn Khải",      "0923450003", "60 Lê Duẩn, Đà Nẵng",             True,  90),
        ("ngothilananh",  "ngothilananh@gmail.com",  "Ngô Thị Lan Anh",    "0934560004", "11 Trần Phú, Hội An",             True,  15),
        ("dinhvanminh",   "dinhvanminh@gmail.com",   "Đinh Văn Minh",      "0945670005", "29 Bà Triệu, Hà Nội",             True,  35),
        ("caothinha",     "caothinha@gmail.com",     "Cao Thị Nhã",        "0956780006", "4 Nguyễn Công Trứ, TP.HCM",       True,  30),
        ("luongvanon",    "luongvanon@gmail.com",    "Lương Văn On",       "0967890007", "82 Lê Thánh Tôn, Bình Dương",     True,  42),
        ("vothiphuong",   "vothiphuong2@gmail.com",  "Võ Thị Phương",      "0978900008", "6 Cách Mạng Tháng Tám, TP.HCM",   True,  28),
        ("nguyenvanquan",  "nguyenvanquan@gmail.com","Nguyễn Văn Quân",    "0989010009", "37 Điện Biên Phủ, Hà Nội",        True,  32),
        ("levanrong",     "levanrong@gmail.com",     "Lê Văn Rồng",        "0990120010", "50 Hoàng Văn Thụ, Thái Nguyên",   True,  44),
        ("phamthisam",    "phamthisam@gmail.com",    "Phạm Thị Sam",       "0901230011", "19 Phan Châu Trinh, Đà Nẵng",     True, 100),
        ("tranvantam",    "tranvantam@gmail.com",    "Trần Văn Tâm",       "0912340012", "8 Quang Trung, Nam Định",          True,  20),
        ("nguyenthiumai", "nguyenthiumai@gmail.com", "Nguyễn Thị Ú Mai",   "0923450013", "41 Nguyễn Văn Cừ, Hà Nội",       True,  25),
        ("hoangvanviet",  "hoangvanviet@gmail.com",  "Hoàng Văn Việt",     "0934560014", "2 Lý Nam Đế, Hà Nội",             True,  18),
        ("vuquocxuong",   "vuquocxuong@gmail.com",   "Vũ Quốc Xương",      "0945670015", "73 Nguyễn Khuyến, Hà Nội",        True,  22),
        # Deactivated users (4 accounts)
        ("tranvanz_old",  "tranvanz.old@gmail.com",  "Trần Văn Zeta (cũ)", "0956780016", "9 Phạm Ngũ Lão, TP.HCM",          False, 200),
        ("lethiyeu_ban",  "lethiyeu.ban@gmail.com",  "Lê Thị Yêu (khóa)", "0967890017", "24 Mai Thị Lựu, TP.HCM",          False, 180),
        ("daoducdat_off", "daoducdat.off@gmail.com", "Đào Đức Đạt (cũ)",  "0978900018", "16 Đinh Lễ, Hà Nội",              False, 220),
        ("buithibao_del", "buithibao.del@gmail.com", "Bùi Thị Bảo (khóa)","0989010019", "5 Tôn Đức Thắng, TP.HCM",         False, 190),
    ]

    readers: list[User] = []
    for username, email, full_name, phone, address, active, joined_days_ago in readers_data:
        u = User(
            username=username,
            email=email,
            password_hash=pw_reader,
            full_name=full_name,
            phone=phone,
            address=address,
            role=UserRole.READER,
            status=UserStatus.ACTIVE if active else UserStatus.INACTIVE,
            created_at=datetime.now(timezone.utc) - timedelta(days=joined_days_ago),
        )
        readers.append(u)

    session.add_all([admin, lib1, lib2, *readers])
    await session.flush()
    print(f"  Created {3 + len(readers)} users ({sum(1 for *_, a, _d in readers_data if not a)} deactivated).")

    # ------------------------------------------------------------------
    # CATEGORIES  (match IDs 1–7 from migration)
    # ------------------------------------------------------------------
    categories = [
        Category(name="Văn học Việt Nam", description="Tác phẩm văn học Việt Nam"),
        Category(name="Khoa học & Công nghệ", description="Sách khoa học và kỹ thuật"),
        Category(name="Lịch sử", description="Lịch sử Việt Nam và thế giới"),
        Category(name="Kinh tế", description="Kinh tế, quản trị, tài chính"),
        Category(name="Ngoại ngữ", description="Sách học ngoại ngữ"),
        Category(name="Thiếu nhi", description="Sách dành cho trẻ em"),
        Category(name="Khoa học máy tính", description="Programming and software engineering"),
    ]
    session.add_all(categories)
    await session.flush()
    print(f"  Created {len(categories)} categories.")

    c = {cat.name: cat for cat in categories}

    # ------------------------------------------------------------------
    # BOOKS  (≥70, spread across all 7 categories)
    # ------------------------------------------------------------------
    VI = BookLanguage.VIETNAMESE
    EN = BookLanguage.ENGLISH
    AV = BookStatus.AVAILABLE

    books_data = [
        # ── Văn học Việt Nam (12) ──────────────────────────────────────
        dict(title="Số Đỏ", author="Vũ Trọng Phụng",
             isbn="978-604-1-10001-1", publisher="NXB Văn học", publication_year=1936,
             language=VI, quantity=4, available_quantity=4,
             description="Tiểu thuyết trào phúng kinh điển của văn học Việt Nam.",
             category_id=c["Văn học Việt Nam"].id),
        dict(title="Chí Phèo", author="Nam Cao",
             isbn="978-604-1-10002-2", publisher="NXB Văn học", publication_year=1941,
             language=VI, quantity=5, available_quantity=5,
             description="Truyện ngắn nổi tiếng về bi kịch người nông dân.",
             category_id=c["Văn học Việt Nam"].id),
        dict(title="Tắt Đèn", author="Ngô Tất Tố",
             isbn="978-604-1-10003-3", publisher="NXB Văn học", publication_year=1939,
             language=VI, quantity=3, available_quantity=3,
             description="Tác phẩm hiện thực phê phán về chế độ sưu thuế.",
             category_id=c["Văn học Việt Nam"].id),
        dict(title="Nỗi Buồn Chiến Tranh", author="Bảo Ninh",
             isbn="978-604-1-10004-4", publisher="NXB Hội Nhà văn", publication_year=1991,
             language=VI, quantity=4, available_quantity=4,
             description="Tiểu thuyết kinh điển về chiến tranh Việt Nam.",
             category_id=c["Văn học Việt Nam"].id),
        dict(title="Đất Rừng Phương Nam", author="Đoàn Giỏi",
             isbn="978-604-1-10005-5", publisher="NXB Kim Đồng", publication_year=1957,
             language=VI, quantity=6, available_quantity=6,
             description="Truyện thiếu nhi đặc sắc về vùng đất Nam Bộ.",
             category_id=c["Văn học Việt Nam"].id),
        dict(title="Mắt Biếc", author="Nguyễn Nhật Ánh",
             isbn="978-604-1-10006-6", publisher="NXB Trẻ", publication_year=1990,
             language=VI, quantity=7, available_quantity=7,
             description="Tiểu thuyết lãng mạn về tình yêu tuổi học trò.",
             category_id=c["Văn học Việt Nam"].id),
        dict(title="Tôi Thấy Hoa Vàng Trên Cỏ Xanh", author="Nguyễn Nhật Ánh",
             isbn="978-604-1-10007-7", publisher="NXB Trẻ", publication_year=2010,
             language=VI, quantity=5, available_quantity=5,
             description="Câu chuyện tuổi thơ đẹp đẽ về tình bạn và gia đình.",
             category_id=c["Văn học Việt Nam"].id),
        dict(title="Lão Hạc", author="Nam Cao",
             isbn="978-604-1-10008-8", publisher="NXB Văn học", publication_year=1943,
             language=VI, quantity=3, available_quantity=3,
             description="Truyện ngắn cảm động về người nông dân nghèo.",
             category_id=c["Văn học Việt Nam"].id),
        dict(title="Vợ Nhặt", author="Kim Lân",
             isbn="978-604-1-10009-9", publisher="NXB Văn học", publication_year=1962,
             language=VI, quantity=4, available_quantity=4,
             description="Truyện ngắn về nạn đói năm 1945 và nhân phẩm con người.",
             category_id=c["Văn học Việt Nam"].id),
        dict(title="Chiếc Lược Ngà", author="Nguyễn Quang Sáng",
             isbn="978-604-1-10010-0", publisher="NXB Văn nghệ", publication_year=1966,
             language=VI, quantity=3, available_quantity=3,
             description="Truyện ngắn cảm động về tình cha con trong chiến tranh.",
             category_id=c["Văn học Việt Nam"].id),
        dict(title="Người Lái Đò Sông Đà", author="Nguyễn Tuân",
             isbn="978-604-1-10011-1", publisher="NXB Văn học", publication_year=1960,
             language=VI, quantity=2, available_quantity=2,
             description="Tuỳ bút xuất sắc về thiên nhiên và con người Tây Bắc.",
             category_id=c["Văn học Việt Nam"].id),
        dict(title="Dấu Chân Người Lính", author="Nguyễn Minh Châu",
             isbn="978-604-1-10012-2", publisher="NXB Quân đội nhân dân", publication_year=1972,
             language=VI, quantity=3, available_quantity=3,
             description="Tiểu thuyết về người lính trong cuộc kháng chiến chống Mỹ.",
             category_id=c["Văn học Việt Nam"].id),

        # ── Khoa học & Công nghệ (10) ──────────────────────────────────
        dict(title="Lập Trình Python Cơ Bản", author="Nguyễn Văn Lập",
             isbn="978-604-2-20001-3", publisher="NXB Thông tin & Truyền thông", publication_year=2022,
             language=VI, quantity=10, available_quantity=10,
             description="Giáo trình Python dành cho người mới bắt đầu.",
             category_id=c["Khoa học & Công nghệ"].id),
        dict(title="Trí Tuệ Nhân Tạo – Nhập Môn", author="Hoàng Kiếm, Đỗ Văn Nhơn",
             isbn="978-604-2-20002-4", publisher="NXB Đại học Quốc gia TP.HCM", publication_year=2020,
             language=VI, quantity=6, available_quantity=6,
             description="Giới thiệu các khái niệm cơ bản về AI và machine learning.",
             category_id=c["Khoa học & Công nghệ"].id),
        dict(title="Khoa Học Dữ Liệu Với Python", author="Lê Thanh Tùng",
             isbn="978-604-2-20003-5", publisher="NXB Thông tin & Truyền thông", publication_year=2021,
             language=VI, quantity=8, available_quantity=8,
             description="Hướng dẫn phân tích dữ liệu với pandas, NumPy, Matplotlib.",
             category_id=c["Khoa học & Công nghệ"].id),
        dict(title="Vật Lý Đại Cương", author="Lương Duyên Bình",
             isbn="978-604-2-20004-6", publisher="NXB Giáo dục", publication_year=2018,
             language=VI, quantity=12, available_quantity=12,
             description="Giáo trình vật lý đại cương dành cho sinh viên kỹ thuật.",
             category_id=c["Khoa học & Công nghệ"].id),
        dict(title="Toán Rời Rạc", author="Nguyễn Đức Nghĩa, Nguyễn Tô Thành",
             isbn="978-604-2-20005-7", publisher="NXB Đại học Quốc gia Hà Nội", publication_year=2019,
             language=VI, quantity=9, available_quantity=9,
             description="Cơ sở toán học cho khoa học máy tính.",
             category_id=c["Khoa học & Công nghệ"].id),
        dict(title="Cấu Trúc Dữ Liệu & Giải Thuật", author="Đinh Mạnh Tường",
             isbn="978-604-2-20006-8", publisher="NXB Khoa học Kỹ thuật", publication_year=2017,
             language=VI, quantity=7, available_quantity=7,
             description="Nghiên cứu các thuật toán và cấu trúc dữ liệu cơ bản.",
             category_id=c["Khoa học & Công nghệ"].id),
        dict(title="Mạng Máy Tính", author="Nguyễn Thúc Hải",
             isbn="978-604-2-20007-9", publisher="NXB Khoa học Kỹ thuật", publication_year=2016,
             language=VI, quantity=5, available_quantity=5,
             description="Giáo trình mạng máy tính và truyền dữ liệu.",
             category_id=c["Khoa học & Công nghệ"].id),
        dict(title="Hệ Điều Hành", author="Nguyễn Kim Khánh",
             isbn="978-604-2-20008-0", publisher="NXB Bách Khoa Hà Nội", publication_year=2018,
             language=VI, quantity=6, available_quantity=6,
             description="Giáo trình hệ điều hành cho sinh viên CNTT.",
             category_id=c["Khoa học & Công nghệ"].id),
        dict(title="Điện Tử Cơ Bản", author="Đỗ Xuân Thụ",
             isbn="978-604-2-20009-1", publisher="NXB Giáo dục", publication_year=2015,
             language=VI, quantity=4, available_quantity=4,
             description="Lý thuyết và thực hành điện tử analog và digital.",
             category_id=c["Khoa học & Công nghệ"].id),
        dict(title="Công Nghệ Sinh Học Đại Cương", author="Nguyễn Như Hiền",
             isbn="978-604-2-20010-2", publisher="NXB Giáo dục", publication_year=2019,
             language=VI, quantity=5, available_quantity=5,
             description="Giới thiệu các lĩnh vực của công nghệ sinh học hiện đại.",
             category_id=c["Khoa học & Công nghệ"].id),

        # ── Lịch sử (10) ──────────────────────────────────────────────
        dict(title="Đại Việt Sử Ký Toàn Thư", author="Ngô Sĩ Liên (biên soạn, tóm tắt)",
             isbn="978-604-3-30001-1", publisher="NXB Khoa học Xã hội", publication_year=2017,
             language=VI, quantity=4, available_quantity=4,
             description="Bộ sử ký lớn nhất thời phong kiến Việt Nam.",
             category_id=c["Lịch sử"].id),
        dict(title="Lịch Sử Việt Nam", author="Nhiều tác giả",
             isbn="978-604-3-30002-2", publisher="NXB Giáo dục", publication_year=2019,
             language=VI, quantity=6, available_quantity=6,
             description="Bộ sách lịch sử Việt Nam từ thời dựng nước đến nay.",
             category_id=c["Lịch sử"].id),
        dict(title="Lịch Sử Thế Giới Cổ Đại", author="Lương Ninh",
             isbn="978-604-3-30003-3", publisher="NXB Giáo dục", publication_year=2016,
             language=VI, quantity=5, available_quantity=5,
             description="Lịch sử các nền văn minh cổ đại trên thế giới.",
             category_id=c["Lịch sử"].id),
        dict(title="Chiến Tranh và Hoà Bình – Góc Nhìn Lịch Sử", author="Dương Trung Quốc",
             isbn="978-604-3-30004-4", publisher="NXB Chính trị Quốc gia", publication_year=2018,
             language=VI, quantity=3, available_quantity=3,
             description="Phân tích lịch sử các cuộc chiến tranh và bài học hoà bình.",
             category_id=c["Lịch sử"].id),
        dict(title="Hồ Chí Minh – Toàn Tập", author="Hồ Chí Minh",
             isbn="978-604-3-30005-5", publisher="NXB Chính trị Quốc gia", publication_year=2011,
             language=VI, quantity=3, available_quantity=3,
             description="Tuyển tập toàn bộ tư tưởng, bài viết của Hồ Chí Minh.",
             category_id=c["Lịch sử"].id),
        dict(title="Lịch Sử Nhà Nguyễn", author="Nguyễn Thế Anh",
             isbn="978-604-3-30006-6", publisher="NXB Văn hoá Thông tin", publication_year=2014,
             language=VI, quantity=4, available_quantity=4,
             description="Nghiên cứu về vương triều Nguyễn – triều đại cuối cùng của Việt Nam.",
             category_id=c["Lịch sử"].id),
        dict(title="Thế Giới Phẳng", author="Thomas L. Friedman",
             isbn="978-0-374-29279-9", publisher="Farrar, Straus and Giroux", publication_year=2005,
             language=EN, quantity=3, available_quantity=3,
             description="A brief history of the twenty-first century globalisation.",
             category_id=c["Lịch sử"].id),
        dict(title="Sapiens: Lược Sử Loài Người", author="Yuval Noah Harari (Nguyễn Thanh Hà dịch)",
             isbn="978-604-3-30008-8", publisher="NXB Tri Thức", publication_year=2020,
             language=VI, quantity=7, available_quantity=7,
             description="Lịch sử loài người từ thời đồ đá đến thế kỷ 21.",
             category_id=c["Lịch sử"].id),
        dict(title="Lịch Sử Trung Quốc 5000 Năm", author="Lâm Hán Đạt, Tào Dư Chương",
             isbn="978-604-3-30009-9", publisher="NXB Văn học", publication_year=2016,
             language=VI, quantity=4, available_quantity=4,
             description="Tổng quan lịch sử Trung Quốc qua 5000 năm văn minh.",
             category_id=c["Lịch sử"].id),
        dict(title="Nghìn Năm Áo Mũ", author="Trần Quang Đức",
             isbn="978-604-3-30010-0", publisher="NXB Thế Giới", publication_year=2013,
             language=VI, quantity=3, available_quantity=3,
             description="Nghiên cứu trang phục cung đình Việt Nam qua các triều đại.",
             category_id=c["Lịch sử"].id),

        # ── Kinh tế (10) ──────────────────────────────────────────────
        dict(title="Kinh Tế Học Vi Mô", author="Robert S. Pindyck (Lê Hoàng Long dịch)",
             isbn="978-604-4-40001-1", publisher="NXB Thống kê", publication_year=2021,
             language=VI, quantity=8, available_quantity=8,
             description="Giáo trình kinh tế vi mô bậc đại học.",
             category_id=c["Kinh tế"].id),
        dict(title="Cha Giàu Cha Nghèo", author="Robert T. Kiyosaki (Nguyễn Dương dịch)",
             isbn="978-604-4-40002-2", publisher="NXB Trẻ", publication_year=2018,
             language=VI, quantity=10, available_quantity=10,
             description="Bí quyết làm giàu và tư duy tài chính cá nhân.",
             category_id=c["Kinh tế"].id),
        dict(title="Đắc Nhân Tâm", author="Dale Carnegie (Nguyễn Hiến Lê dịch)",
             isbn="978-604-4-40003-3", publisher="NXB Tổng hợp TP.HCM", publication_year=2019,
             language=VI, quantity=12, available_quantity=12,
             description="Nghệ thuật giao tiếp và thuyết phục con người.",
             category_id=c["Kinh tế"].id),
        dict(title="Nghĩ Giàu Làm Giàu", author="Napoleon Hill (Đinh Tuyết Mai dịch)",
             isbn="978-604-4-40004-4", publisher="NXB Lao động Xã hội", publication_year=2017,
             language=VI, quantity=6, available_quantity=6,
             description="Triết lý thành công và tư duy làm giàu.",
             category_id=c["Kinh tế"].id),
        dict(title="Quản Trị Học", author="Nguyễn Thị Liên Diệp, Phạm Văn Nam",
             isbn="978-604-4-40005-5", publisher="NXB Lao động Xã hội", publication_year=2020,
             language=VI, quantity=7, available_quantity=7,
             description="Giáo trình quản trị học cho sinh viên kinh tế.",
             category_id=c["Kinh tế"].id),
        dict(title="Marketing Căn Bản", author="Philip Kotler (Vũ Trọng Hùng dịch)",
             isbn="978-604-4-40006-6", publisher="NXB Lao động Xã hội", publication_year=2019,
             language=VI, quantity=9, available_quantity=9,
             description="Giáo trình marketing căn bản được sử dụng rộng rãi.",
             category_id=c["Kinh tế"].id),
        dict(title="Người Khởi Nghiệp Tinh Gọn", author="Eric Ries (Phạm Anh Tuấn dịch)",
             isbn="978-604-4-40007-7", publisher="NXB Trẻ", publication_year=2021,
             language=VI, quantity=5, available_quantity=5,
             description="Phương pháp xây dựng startup bền vững theo mô hình Lean.",
             category_id=c["Kinh tế"].id),
        dict(title="Kế Toán Tài Chính", author="Đặng Thị Loan",
             isbn="978-604-4-40008-8", publisher="NXB Đại học Kinh tế Quốc dân", publication_year=2020,
             language=VI, quantity=8, available_quantity=8,
             description="Giáo trình kế toán tài chính theo chuẩn mực Việt Nam.",
             category_id=c["Kinh tế"].id),
        dict(title="Phân Tích Tài Chính Doanh Nghiệp", author="Nguyễn Năng Phúc",
             isbn="978-604-4-40009-9", publisher="NXB Đại học Kinh tế Quốc dân", publication_year=2018,
             language=VI, quantity=5, available_quantity=5,
             description="Phân tích báo cáo tài chính và đánh giá hiệu quả doanh nghiệp.",
             category_id=c["Kinh tế"].id),
        dict(title="The Intelligent Investor", author="Benjamin Graham",
             isbn="978-0-06-055566-5", publisher="HarperBusiness", publication_year=2006,
             language=EN, quantity=4, available_quantity=4,
             description="The definitive book on value investing.",
             category_id=c["Kinh tế"].id),

        # ── Ngoại ngữ (8) ─────────────────────────────────────────────
        dict(title="Tiếng Anh Giao Tiếp Hàng Ngày", author="Nguyễn Bằng Phi",
             isbn="978-604-5-50001-1", publisher="NXB Đại học Quốc gia Hà Nội", publication_year=2021,
             language=VI, quantity=10, available_quantity=10,
             description="Sách luyện kỹ năng giao tiếp tiếng Anh thực tế.",
             category_id=c["Ngoại ngữ"].id),
        dict(title="Ngữ Pháp Tiếng Anh Thực Hành", author="Huỳnh Văn Sơn",
             isbn="978-604-5-50002-2", publisher="NXB Tổng hợp TP.HCM", publication_year=2020,
             language=VI, quantity=8, available_quantity=8,
             description="Hệ thống ngữ pháp tiếng Anh từ cơ bản đến nâng cao.",
             category_id=c["Ngoại ngữ"].id),
        dict(title="TOEIC 900 – Chinh Phục Điểm Cao", author="Kim Se Ryung (Phương Thảo dịch)",
             isbn="978-604-5-50003-3", publisher="NXB Lao động Xã hội", publication_year=2022,
             language=VI, quantity=15, available_quantity=15,
             description="Luyện thi TOEIC với bộ đề và chiến lược làm bài.",
             category_id=c["Ngoại ngữ"].id),
        dict(title="Giáo Trình Tiếng Trung Sơ Cấp", author="Khoa Tiếng Trung – ĐHNN Hà Nội",
             isbn="978-604-5-50004-4", publisher="NXB Đại học Quốc gia Hà Nội", publication_year=2019,
             language=VI, quantity=7, available_quantity=7,
             description="Giáo trình tiếng Trung Quốc dành cho người mới bắt đầu.",
             category_id=c["Ngoại ngữ"].id),
        dict(title="Tiếng Nhật Sơ Cấp (Minna no Nihongo I)", author="3A Corporation",
             isbn="978-4-88319-102-8", publisher="3A Corporation", publication_year=2020,
             language=VI, quantity=6, available_quantity=6,
             description="Giáo trình tiếng Nhật phổ biến nhất cho người Việt.",
             category_id=c["Ngoại ngữ"].id),
        dict(title="Từ Điển Việt – Anh", author="Bùi Phụng",
             isbn="978-604-5-50006-6", publisher="NXB Thế Giới", publication_year=2018,
             language=VI, quantity=5, available_quantity=5,
             description="Từ điển Việt – Anh thông dụng với hơn 50.000 từ.",
             category_id=c["Ngoại ngữ"].id),
        dict(title="English Grammar in Use", author="Raymond Murphy",
             isbn="978-1-108-45765-3", publisher="Cambridge University Press", publication_year=2019,
             language=EN, quantity=8, available_quantity=8,
             description="A self-study reference and practice book for intermediate learners.",
             category_id=c["Ngoại ngữ"].id),
        dict(title="Tiếng Hàn Cho Người Mới Bắt Đầu", author="Bùi Thị Thoa",
             isbn="978-604-5-50008-8", publisher="NXB Đại học Quốc gia Hà Nội", publication_year=2021,
             language=VI, quantity=6, available_quantity=6,
             description="Giáo trình tiếng Hàn căn bản với bảng chữ cái và hội thoại.",
             category_id=c["Ngoại ngữ"].id),

        # ── Thiếu nhi (10) ────────────────────────────────────────────
        dict(title="Dế Mèn Phiêu Lưu Ký", author="Tô Hoài",
             isbn="978-604-6-60001-1", publisher="NXB Kim Đồng", publication_year=1941,
             language=VI, quantity=8, available_quantity=8,
             description="Truyện dài nổi tiếng về cuộc phiêu lưu của chú Dế Mèn.",
             category_id=c["Thiếu nhi"].id),
        dict(title="Kính Vạn Hoa", author="Nguyễn Nhật Ánh",
             isbn="978-604-6-60002-2", publisher="NXB Kim Đồng", publication_year=1995,
             language=VI, quantity=6, available_quantity=6,
             description="Bộ truyện thiếu nhi dài về cuộc sống học trò.",
             category_id=c["Thiếu nhi"].id),
        dict(title="Hoàng Tử Bé", author="Antoine de Saint-Exupéry (Bùi Giáng dịch)",
             isbn="978-604-6-60003-3", publisher="NXB Hội Nhà văn", publication_year=2019,
             language=VI, quantity=9, available_quantity=9,
             description="Câu chuyện triết học dành cho cả trẻ em và người lớn.",
             category_id=c["Thiếu nhi"].id),
        dict(title="Những Cuộc Phiêu Lưu Của Tom Sawyer",
             author="Mark Twain (Nguyễn Thành Long dịch)",
             isbn="978-604-6-60004-4", publisher="NXB Kim Đồng", publication_year=2018,
             language=VI, quantity=5, available_quantity=5,
             description="Câu chuyện phiêu lưu của cậu bé tinh nghịch Tom Sawyer.",
             category_id=c["Thiếu nhi"].id),
        dict(title="Hai Vạn Dặm Dưới Đáy Biển", author="Jules Verne (Lê Xuân Nhị dịch)",
             isbn="978-604-6-60005-5", publisher="NXB Kim Đồng", publication_year=2017,
             language=VI, quantity=4, available_quantity=4,
             description="Hành trình khám phá đại dương kỳ bí cùng thuyền trưởng Nemo.",
             category_id=c["Thiếu nhi"].id),
        dict(title="Alice Ở Xứ Sở Thần Tiên", author="Lewis Carroll (Đổng Đức Thịnh dịch)",
             isbn="978-604-6-60006-6", publisher="NXB Kim Đồng", publication_year=2020,
             language=VI, quantity=5, available_quantity=5,
             description="Câu chuyện phiêu lưu kỳ diệu của cô bé Alice.",
             category_id=c["Thiếu nhi"].id),
        dict(title="Doremon – Tuyển Tập Đặc Biệt", author="Fujiko F. Fujio",
             isbn="978-604-6-60007-7", publisher="NXB Kim Đồng", publication_year=2021,
             language=VI, quantity=10, available_quantity=10,
             description="Tuyển tập những câu chuyện hay nhất về chú mèo máy Doraemon.",
             category_id=c["Thiếu nhi"].id),
        dict(title="Thám Tử Lừng Danh Conan – Vol.1", author="Gosho Aoyama",
             isbn="978-604-6-60008-8", publisher="NXB Kim Đồng", publication_year=2022,
             language=VI, quantity=7, available_quantity=7,
             description="Truyện tranh trinh thám nổi tiếng về cậu bé thám tử Conan.",
             category_id=c["Thiếu nhi"].id),
        dict(title="Truyện Cổ Grimm", author="Anh em Grimm (Nguyễn Văn Hạnh dịch)",
             isbn="978-604-6-60009-9", publisher="NXB Văn học", publication_year=2019,
             language=VI, quantity=6, available_quantity=6,
             description="Tuyển tập cổ tích nổi tiếng của anh em nhà Grimm.",
             category_id=c["Thiếu nhi"].id),
        dict(title="Bộ sách Ehon – Cảm xúc của bé", author="Nhiều tác giả Nhật Bản",
             isbn="978-604-6-60010-0", publisher="NXB Đinh Tị", publication_year=2022,
             language=VI, quantity=8, available_quantity=8,
             description="Bộ sách tranh Nhật Bản giúp trẻ nhận biết và quản lý cảm xúc.",
             category_id=c["Thiếu nhi"].id),

        # ── Khoa học máy tính (10) ──────────────────────────────────────
        dict(title="Clean Code", author="Robert C. Martin",
             isbn="978-0-13-235088-4", publisher="Prentice Hall", publication_year=2008,
             language=EN, quantity=5, available_quantity=5,
             description="A handbook of agile software craftsmanship.",
             category_id=c["Khoa học máy tính"].id),
        dict(title="The Pragmatic Programmer", author="David Thomas, Andrew Hunt",
             isbn="978-0-13-595705-9", publisher="Addison-Wesley", publication_year=2019,
             language=EN, quantity=4, available_quantity=4,
             description="Your journey to mastery in software development.",
             category_id=c["Khoa học máy tính"].id),
        dict(title="Design Patterns: Elements of Reusable OO Software",
             author="Gang of Four",
             isbn="978-0-20-163361-5", publisher="Addison-Wesley", publication_year=1994,
             language=EN, quantity=3, available_quantity=3,
             description="The seminal book on software design patterns.",
             category_id=c["Khoa học máy tính"].id),
        dict(title="Introduction to Algorithms (CLRS)", author="Cormen, Leiserson, Rivest, Stein",
             isbn="978-0-26-204630-5", publisher="MIT Press", publication_year=2022,
             language=EN, quantity=4, available_quantity=4,
             description="Comprehensive textbook on algorithms and data structures.",
             category_id=c["Khoa học máy tính"].id),
        dict(title="Giáo Trình Cơ Sở Dữ Liệu", author="Hồ Thuần, Hồ Cẩm Hà",
             isbn="978-604-7-70005-5", publisher="NXB Lao động Xã hội", publication_year=2019,
             language=VI, quantity=7, available_quantity=7,
             description="Thiết kế cơ sở dữ liệu quan hệ và ngôn ngữ SQL.",
             category_id=c["Khoa học máy tính"].id),
        dict(title="Computer Networking: A Top-Down Approach",
             author="James Kurose, Keith Ross",
             isbn="978-0-13-668155-2", publisher="Pearson", publication_year=2021,
             language=EN, quantity=3, available_quantity=3,
             description="Widely-used textbook on computer networking.",
             category_id=c["Khoa học máy tính"].id),
        dict(title="Lập Trình Web Với Django", author="Trần Thị Minh Châu",
             isbn="978-604-7-70007-7", publisher="NXB Thông tin & Truyền thông", publication_year=2022,
             language=VI, quantity=6, available_quantity=6,
             description="Xây dựng ứng dụng web Python với framework Django.",
             category_id=c["Khoa học máy tính"].id),
        dict(title="Docker Deep Dive", author="Nigel Poulton",
             isbn="978-1-52-130931-2", publisher="Independently published", publication_year=2023,
             language=EN, quantity=4, available_quantity=4,
             description="A fast introduction to containers with Docker.",
             category_id=c["Khoa học máy tính"].id),
        dict(title="Refactoring", author="Martin Fowler",
             isbn="978-0-13-468599-1", publisher="Addison-Wesley", publication_year=2018,
             language=EN, quantity=3, available_quantity=3,
             description="Improving the design of existing code.",
             category_id=c["Khoa học máy tính"].id),
        dict(title="Lập Trình Hướng Đối Tượng Với Java", author="Kiet T. Nguyen",
             isbn="978-604-7-70010-0", publisher="NXB Đại học Quốc gia TP.HCM", publication_year=2020,
             language=VI, quantity=8, available_quantity=8,
             description="Lập trình Java từ cơ bản đến hướng đối tượng nâng cao.",
             category_id=c["Khoa học máy tính"].id),
    ]

    books: list[Book] = []
    for bd in books_data:
        b = Book(
            title=bd["title"],
            author=bd["author"],
            isbn=bd.get("isbn"),
            publisher=bd.get("publisher"),
            publication_year=bd.get("publication_year"),
            language=bd["language"],
            description=bd.get("description"),
            quantity=bd["quantity"],
            available_quantity=bd["available_quantity"],
            status=AV,
            category_id=bd["category_id"],
        )
        books.append(b)

    session.add_all(books)
    await session.flush()
    print(f"  Created {len(books)} books.")

    # ------------------------------------------------------------------
    # BORROWINGS  (33 records; ≥20 distinct books touched)
    # r = readers list (index 0–28); b = books list (index 0–69)
    # ------------------------------------------------------------------
    today = date.today()

    def borrow(r_idx: int, b_idx: int, days_ago: int, duration: int,
               returned_after: int | None = None,
               overdue: bool = False,
               fine: float = 0.0,
               renewed: int = 0) -> Borrowing:
        bd = today - timedelta(days=days_ago)
        dd = bd + timedelta(days=duration)
        rd = (bd + timedelta(days=returned_after)) if returned_after is not None else None
        if rd is not None:
            st = BorrowingStatus.RETURNED
        elif overdue:
            st = BorrowingStatus.OVERDUE
        else:
            st = BorrowingStatus.BORROWED
        return Borrowing(
            user_id=readers[r_idx].id,
            book_id=books[b_idx].id,
            borrow_date=bd,
            due_date=dd,
            return_date=rd,
            status=st,
            fine_amount=fine,
            renewed_count=renewed,
        )

    borrowings_raw = [
        # (r_idx, b_idx, days_ago, duration, returned_after, overdue, fine, renewed)
        # ── Active BORROWED ──────────────────────────────────────────
        borrow(0,  0,   3,  14),                             # Số Đỏ
        borrow(1,  2,   5,  14),                             # Lập Trình Python
        borrow(2,  12, 10,  14),                             # Khoa Học Dữ Liệu
        borrow(3,  22,  2,  14),                             # Đắc Nhân Tâm
        borrow(4,  32,  7,  14),                             # TOEIC 900
        borrow(5,  42,  4,  14),                             # Dế Mèn
        borrow(6,  50,  6,  14),                             # Clean Code
        borrow(7,  51,  1,  14),                             # Pragmatic Programmer
        borrow(8,  14,  3,  14),                             # Mạng Máy Tính
        borrow(9,  23,  8,  14),                             # Nghĩ Giàu Làm Giàu
        borrow(10, 43,  9,  14),                             # Kính Vạn Hoa
        borrow(11, 55,  2,  14),                             # Lập Trình Web Django
        borrow(12, 20,  5,  14,  renewed=1),                # Đại Việt Sử Ký
        borrow(13, 30,  3,  14),                             # Kinh Tế Vi Mô
        # ── OVERDUE ──────────────────────────────────────────────────
        borrow(14,  3,  25,  14, overdue=True,
               fine=11 * settings.fine_per_day),             # Nỗi Buồn Chiến Tranh
        borrow(15,  11, 20,  14, overdue=True,
               fine=6  * settings.fine_per_day),             # Điện Tử Cơ Bản
        borrow(16,  21, 30,  14, overdue=True,
               fine=16 * settings.fine_per_day),             # Lịch Sử Thế Giới Cổ Đại
        borrow(17,  31, 18,  14, overdue=True,
               fine=4  * settings.fine_per_day),             # Cha Giàu Cha Nghèo
        borrow(18,  41, 22,  14, overdue=True,
               fine=8  * settings.fine_per_day),             # Hoàng Tử Bé
        borrow(19,  52, 32,  14, overdue=True,
               fine=18 * settings.fine_per_day),             # Design Patterns
        # ── RETURNED ─────────────────────────────────────────────────
        borrow(0,  50,  60,  14, returned_after=13),         # Clean Code – returned on time
        borrow(1,  51,  45,  14, returned_after=14),         # Pragmatic Programmer – exact
        borrow(2,   1,  40,  14, returned_after=20, fine=6 * settings.fine_per_day),
        borrow(3,  22,  35,  14, returned_after=12),         # Đắc Nhân Tâm
        borrow(4,  40,  50,  14, returned_after=14),         # Dế Mèn
        borrow(5,  20,  55,  14, returned_after=13),         # Đại Việt Sử Ký
        borrow(6,  30,  42,  14, returned_after=11),         # Kinh Tế Vi Mô
        borrow(7,  10,  36,  14, returned_after=15, fine=1 * settings.fine_per_day),
        borrow(8,  34,  48,  14, returned_after=13),         # Tiếng Anh Giao Tiếp
        borrow(9,  33,  30,  14, returned_after=10),         # Từ Điển
        borrow(10, 43,  60,  14, returned_after=14),         # Kính Vạn Hoa (earlier)
        borrow(11, 45,  70,  14, returned_after=13),         # Hai Vạn Dặm Dưới Đáy Biển
        borrow(12, 53,  80,  14, returned_after=14),         # CLRS
        borrow(20, 24,  90,  14, returned_after=20, fine=6 * settings.fine_per_day),
    ]                                                        # total = 14 + 6 + 14 = 34

    # Adjust available_quantity for active (non-returned) borrowings
    active_book_indices = {0, 2, 12, 22, 32, 42, 50, 51, 14, 23, 43, 55, 20, 30,
                           3, 11, 21, 31, 41, 52}
    for idx in active_book_indices:
        if books[idx].available_quantity > 0:
            books[idx].available_quantity -= 1

    session.add_all(borrowings_raw)
    await session.flush()
    print(f"  Created {len(borrowings_raw)} borrowing records.")

    # ------------------------------------------------------------------
    # REVIEWS  (0–5 per book; only for books that have been returned)
    # ------------------------------------------------------------------
    # Pairs of (reader_idx, book_idx) that have a completed return
    returned_pairs = [
        (0, 50), (1, 51), (2,  1), (3, 22), (4, 40),
        (5, 20), (6, 30), (7, 10), (8, 34), (9, 33),
        (10, 43), (11, 45), (12, 53), (20, 24),
        (0, 50),  # already added – skip duplicates below
    ]

    review_data = [
        # (book_idx, reader_idx, rating, comment)
        # Clean Code (book 50) – 3 reviews
        (50, 0, 5, "Cuốn sách tuyệt vời về cách viết code sạch, rất hữu ích!"),
        (50, 2, 4, "Nội dung chắc chắn, một số ví dụ hơi cũ nhưng vẫn áp dụng được."),
        (50, 7, 5, "Must-read for every developer. Changed how I think about code quality."),

        # The Pragmatic Programmer (book 51) – 2 reviews
        (51, 1, 5, "Sách lập trình hay nhất tôi từng đọc. Rất thực tiễn."),
        (51, 6, 4, "Great advice on software craftsmanship. Highly recommended."),

        # Chí Phèo (book 1) – 2 reviews
        (1, 2, 4, "Tác phẩm hay, phân tích tâm lý nhân vật rất sâu sắc."),
        (1, 9, 5, "Kinh điển văn học Việt Nam. Đọc đi đọc lại vẫn thấy hay."),

        # Đắc Nhân Tâm (book 22) – 3 reviews
        (22, 3, 5, "Sách thay đổi cách tôi giao tiếp và xây dựng quan hệ."),
        (22, 8, 4, "Nhiều bài học quý, nên đọc lại nhiều lần."),
        (22, 0, 3, "Hay nhưng nhiều ví dụ đã cũ, cần cập nhật hơn."),

        # Dế Mèn Phiêu Lưu Ký (book 40, Thiếu nhi)
        (40, 4, 5, "Tuổi thơ của tôi gắn với cuốn sách này. Tuyệt vời!"),

        # Đại Việt Sử Ký (book 20) – 1 review
        (20, 5, 4, "Tư liệu lịch sử quý báu. Bản dịch dễ đọc."),

        # Kinh Tế Vi Mô (book 30) – 2 reviews
        (30, 6, 4, "Giáo trình chuẩn, ví dụ minh hoạ rõ ràng."),
        (30, 3, 3, "Khá nặng lý thuyết, cần thêm bài tập thực hành."),

        # Vật Lý Đại Cương (book 10) – 1 review
        (10, 7, 3, "Đầy đủ lý thuyết nhưng bài tập hơi ít."),

        # Tiếng Anh Giao Tiếp (book 34)
        (34, 8, 5, "Rất thực dụng, giúp nói chuyện tự tin hơn hẳn."),

        # Từ Điển Việt – Anh (book 33) – 1 review
        (33, 9, 4, "Tin dùng hàng ngày, tra cứu nhanh và chính xác."),

        # Kính Vạn Hoa (book 43) – 2 reviews
        (43, 10, 5, "Bộ sách thiếu nhi hay nhất, đọc cả 45 tập không chán."),
        (43, 4, 4, "Nguyễn Nhật Ánh viết rất gần gũi với trẻ em."),

        # Hai Vạn Dặm (book 45) – 1 review
        (45, 11, 5, "Phiêu lưu kỳ thú, trí tưởng tượng phong phú của Jules Verne."),

        # CLRS (book 53) – 2 reviews
        (53, 12, 4, "Comprehensive and rigorous. Essential for CS students."),
        (53, 0, 3, "Very dense. Best used as a reference rather than read cover to cover."),

        # Nghĩ Giàu Làm Giàu (book 24) – 1 review
        (24, 20, 4, "Nhiều bài học truyền cảm hứng về tư duy thành công."),
    ]

    reviews: list[Review] = []
    seen: set[tuple[int, int]] = set()
    for book_idx, reader_idx, rating, comment in review_data:
        key = (books[book_idx].id, readers[reader_idx].id)
        if key in seen:
            continue
        seen.add(key)
        reviews.append(Review(
            book_id=books[book_idx].id,
            user_id=readers[reader_idx].id,
            rating=rating,
            comment=comment,
            status=ReviewStatus.ACTIVE,
        ))

    session.add_all(reviews)
    await session.flush()
    print(f"  Created {len(reviews)} reviews.")

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
