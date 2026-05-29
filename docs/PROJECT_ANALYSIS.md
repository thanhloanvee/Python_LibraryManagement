# PROJECT_ANALYSIS.md — Hệ Thống Quản Lý Thư Viện

---

## 1. Project Overview

**Tên dự án:** Hệ Thống Quản Lý Thư Viện (Library Management System — LMS)

**Mục đích:**
Xây dựng một hệ thống quản lý thư viện trực tuyến full-stack bằng Python, cho phép độc giả tìm kiếm và theo dõi sách mượn, thủ thư xử lý toàn bộ lưu thông sách, và quản trị viên quản lý kho sách, người dùng và theo dõi hiệu quả hoạt động qua dashboard thống kê.

**Đối tượng sử dụng:**
- **Độc giả (Reader):** Người dùng cuối — tìm kiếm, xem thông tin sách, theo dõi phiếu mượn, gia hạn và đánh giá sách
- **Thủ thư (Librarian):** Nhân viên thư viện — cấp phát sách, xử lý trả sách, theo dõi phiếu mượn và phí phạt
- **Quản trị viên (Admin):** Quản lý toàn bộ hệ thống — kho sách, thể loại, người dùng, báo cáo thống kê

**Mục tiêu chính:**
- Số hoá quy trình mượn/trả sách, thay thế hoàn toàn sổ sách giấy
- Kiểm soát tồn kho sách theo thời gian thực
- Tự động tính phí phạt khi trả sách quá hạn
- Cung cấp thống kê và biểu đồ hoạt động cho ban quản lý
- Cho phép độc giả tìm kiếm, lọc và đánh giá sách trực tuyến

---

## 2. Business Context

**Vấn đề cần giải quyết:**
Thư viện truyền thống quản lý sách và phiếu mượn thủ công bằng giấy tờ, dẫn đến khó kiểm soát tồn kho theo thời gian thực, dễ thất thoát thông tin, không có báo cáo tổng hợp tức thời và khó theo dõi sách quá hạn để thu phí phạt.

**Lý do xây dựng hệ thống:**
Đồ án được thiết kế và xây dựng từ đầu bằng Python với mục tiêu:
- Áp dụng các công nghệ Python hiện đại (FastAPI, SQLAlchemy async, Pydantic v2) vào bài toán quản lý thực tế
- Thiết kế kiến trúc phân tầng rõ ràng (layered architecture) để dễ bảo trì và mở rộng
- Cung cấp đồng thời REST API và giao diện web server-side rendering trong một ứng dụng duy nhất
- Thực hành quy trình phát triển phần mềm chuẩn: migration DB, unit test, environment config, RBAC

**Lợi ích kỳ vọng:**
- Giảm thời gian xử lý mượn/trả sách
- Loại bỏ sai sót thủ công trong quản lý tồn kho
- Tự động hoá tính phí phạt sách trễ theo cấu hình linh hoạt
- Cung cấp số liệu thống kê trực quan phục vụ ban quản lý thư viện

---

## 3. System Overview

### Kiến trúc tổng thể

Hệ thống theo kiến trúc **Monolith Full-stack**, một server FastAPI duy nhất phục vụ cả giao diện Web UI (SSR) và REST API:

```
[Trình duyệt Web]
      │
      ├─ Web UI (HTML/Jinja2 + HTMX + Alpine.js)
      │       └─ /web/* routes — Server-Side Rendering
      │
      └─ REST API (JSON)
              └─ /api/v1/* routes
                        │
               [FastAPI Application]
                        │
             ┌──────────┴──────────┐
        [Services Layer]    [Repository Layer]
             │                     │
        [ORM Models]        [SQLAlchemy Async]
             │
        [SQLite — library.db]
```

### Các module chính

| Module | Đường dẫn | Trách nhiệm |
|---|---|---|
| API v1 | `app/api/v1/` | REST JSON API endpoints |
| Web UI | `app/web/` | Server-rendered HTML pages (Jinja2) |
| Services | `app/services/` | Business logic — kiểm tra quy tắc nghiệp vụ |
| Repositories | `app/repositories/` | Data access layer — truy vấn DB async |
| Models | `app/models/` | SQLAlchemy ORM entities |
| Schemas | `app/schemas/` | Pydantic v2 — validation & serialization |
| Core | `app/core/` | Config (pydantic-settings), Security (JWT, bcrypt) |
| DB | `app/db/` | Engine async, session factory, DeclarativeBase |
| Middleware | `app/middleware/` | Access log middleware |
| Templates | `app/templates/` | Jinja2 HTML templates |
| Dependencies | `app/dependencies/` | FastAPI DI — xác thực JWT (API) và RBAC |

### Trách nhiệm từng tầng

- **API / Web Layer:** Tiếp nhận HTTP request, validate đầu vào qua Pydantic, gọi service tương ứng, trả JSON hoặc render HTML
- **Service Layer:** Toàn bộ business logic — kiểm tra quy tắc nghiệp vụ trước khi thao tác DB
- **Repository Layer:** Truy vấn database thuần túy (async), không chứa logic nghiệp vụ
- **Model Layer:** Định nghĩa ORM entity và các helper property (is_available, is_overdue, calculate_fine…)
- **Dependencies:** Dependency injection — xác thực JWT Bearer token (API) và httponly cookie (Web), kiểm tra role RBAC

---

## 4. Technology Stack

### Ngôn ngữ lập trình

| Công nghệ | Phiên bản | Vai trò |
|---|---|---|
| **Python** | 3.12+ | Ngôn ngữ lập trình chính — toàn bộ backend |

### Framework & Runtime

| Công nghệ | Phiên bản | Vai trò |
|---|---|---|
| **FastAPI** | ≥ 0.111.0 | Web framework bất đồng bộ (async/await), xây dựng REST API và Web UI, tích hợp sẵn Swagger UI |
| **Uvicorn** | ≥ 0.29.0 | ASGI server — chạy ứng dụng FastAPI trong production và development |

### Database & ORM

| Công nghệ | Phiên bản | Vai trò |
|---|---|---|
| **SQLite** | Built-in | Cơ sở dữ liệu quan hệ nhẹ, lưu toàn bộ dữ liệu trong file `library.db` |
| **SQLAlchemy** | ≥ 2.0.30 | ORM bất đồng bộ (async) — ánh xạ Python class ↔ bảng DB, viết truy vấn theo kiểu Pythonic |
| **aiosqlite** | ≥ 0.20.0 | Driver async cho SQLite, cho phép chạy query không blocking |
| **Alembic** | ≥ 1.13.1 | Công cụ migration schema database — quản lý phiên bản schema qua script Python |

### Xác thực & Bảo mật

| Công nghệ | Phiên bản | Vai trò |
|---|---|---|
| **PyJWT** | ≥ 2.8.0 | Tạo và xác thực JSON Web Token (access token + refresh token) |
| **bcrypt** | ≥ 4.0.0 | Hash mật khẩu người dùng bằng thuật toán bcrypt (industry standard) |
| **itsdangerous** | ≥ 2.1.2 | Ký và xác thực dữ liệu cookie flash message |

### Validation & Cấu hình

| Công nghệ | Phiên bản | Vai trò |
|---|---|---|
| **Pydantic v2** | ≥ 2.8.0 | Schema validation và serialization cho API request/response |
| **pydantic-settings** | ≥ 2.3.0 | Đọc cấu hình hệ thống từ file `.env` với type safety |
| **email-validator** | ≥ 2.1.1 | Xác thực định dạng email trong schema Pydantic |

### Giao diện & Templating

| Công nghệ | Phiên bản | Vai trò |
|---|---|---|
| **Jinja2** | ≥ 3.1.4 | Template engine — render HTML phía server (SSR), tích hợp sẵn với FastAPI |
| **HTMX** | 1.9.12 (CDN) | Xử lý partial page update (live search, dynamic rows) mà không cần viết JavaScript thuần |
| **Alpine.js** | 3.x (CDN) | Reactivity nhẹ phía client — dropdown, sidebar toggle, UI state đơn giản |
| **TailwindCSS** | CDN Play (JIT) | CSS utility-first — styling toàn bộ giao diện, responsive |
| **Chart.js** | 4 (CDN) | Vẽ biểu đồ thống kê cột (borrow/return theo tháng) trên admin dashboard |
| **python-multipart** | ≥ 0.0.9 | Parse form data và file upload trong FastAPI |
| **aiofiles** | ≥ 23.2.1 | Xử lý file I/O bất đồng bộ khi upload ảnh bìa sách |

### Testing & Công cụ phát triển

| Công nghệ | Phiên bản | Vai trò |
|---|---|---|
| **pytest** | ≥ 8.2.0 | Framework kiểm thử đơn vị và tích hợp |
| **pytest-asyncio** | ≥ 0.23.6 | Hỗ trợ test async function với pytest |
| **httpx** | ≥ 0.27.0 | HTTP client bất đồng bộ — dùng trong integration tests để gọi FastAPI |
| **Ruff** | ≥ 0.4.4 | Linting và formatting code Python (thay thế flake8 + black) |

---

## 5. Project Structure

```
Python_LibraryManagement/
├── .env                        # Biến môi trường (git-ignored)
├── .env.example                # Template hướng dẫn cấu hình
├── requirements.txt            # Danh sách dependencies Python
├── README.md                   # Tài liệu dự án
├── docs/                       # Tài liệu phân tích & trình bày
└── backend/
    ├── alembic.ini             # Cấu hình Alembic migration
    ├── pytest.ini              # Cấu hình pytest
    ├── seed.py                 # Script tạo dữ liệu mẫu
    ├── library.db              # File SQLite database (tự tạo khi chạy)
    ├── alembic/
    │   └── versions/
    │       └── 001_initial_schema.py  # Migration khởi tạo toàn bộ schema DB
    ├── tests/
    │   ├── conftest.py         # Fixtures dùng chung (test DB, test client)
    │   ├── test_auth.py        # Test đăng ký, đăng nhập, JWT flow
    │   ├── test_books.py       # Test CRUD sách, phân quyền
    │   └── test_borrowings.py  # Test mượn/trả, gia hạn, phí phạt
    └── app/
        ├── main.py             # App factory (create_app), lifespan, middleware setup
        ├── core/
        │   ├── config.py       # Settings — pydantic-settings đọc .env, lru_cache singleton
        │   └── security.py     # JWT helpers (create/verify), bcrypt hash/verify
        ├── db/
        │   ├── base.py         # DeclarativeBase SQLAlchemy — base cho tất cả ORM models
        │   └── session.py      # Async engine, AsyncSessionLocal, get_db() dependency
        ├── models/             # SQLAlchemy ORM models — 5 entity
        │   ├── user.py         # User (UserRole enum, UserStatus enum, is_active property)
        │   ├── book.py         # Book (BookStatus, BookLanguage, is_available property)
        │   ├── category.py     # Category
        │   ├── borrowing.py    # Borrowing (BorrowingStatus, BookCondition, calculate_fine())
        │   └── review.py       # Review (unique constraint user_id + book_id)
        ├── schemas/            # Pydantic v2 schemas (request/response DTO)
        │   ├── auth.py         # LoginRequest, TokenResponse, RegisterRequest
        │   ├── book.py         # BookCreate, BookUpdate, BookResponse
        │   ├── borrowing.py    # BorrowingCreate, ReturnBookRequest, BorrowingFilter
        │   ├── category.py     # CategoryCreate, CategoryUpdate, CategoryResponse
        │   ├── dashboard.py    # DashboardStats, PopularBook, ActiveReader, MonthlyBorrowingStat
        │   ├── review.py       # ReviewCreate, ReviewResponse
        │   ├── user.py         # UserCreate, UserUpdate, UserResponse
        │   └── common.py       # PaginatedResponse[T], PaginationMeta, MessageResponse
        ├── repositories/       # Data access layer — async DB queries, không có business logic
        │   ├── book.py
        │   ├── borrowing.py
        │   ├── category.py
        │   ├── review.py
        │   └── user.py
        ├── services/           # Business logic layer — kiểm tra quy tắc trước khi thao tác DB
        │   ├── auth.py         # Login, register, refresh token, change password
        │   ├── book.py         # CRUD sách, kiểm tra tồn kho, upload ảnh bìa
        │   ├── borrowing.py    # Issue, return, renew, fine, sync overdue
        │   ├── category.py     # CRUD thể loại
        │   ├── dashboard.py    # KPI aggregation, biểu đồ theo tháng, top sách/độc giả
        │   ├── review.py       # Tạo/cập nhật review, kiểm tra quyền
        │   └── user.py         # Quản lý người dùng (role, status, delete)
        ├── dependencies/
        │   ├── auth.py         # get_current_user — xác thực JWT Bearer token
        │   └── rbac.py         # require_reader / require_librarian / require_admin
        ├── middleware/
        │   └── logging.py      # Access log middleware — ghi log mọi HTTP request
        ├── api/v1/             # REST API routers — prefix /api/v1/
        │   ├── router.py       # Tập hợp tất cả API sub-routers
        │   ├── auth.py         # /auth/login, /register, /refresh, /me, /change-password
        │   ├── books.py        # CRUD /books, filter, search
        │   ├── borrowings.py   # /borrowings — issue, return, renew, mark-fine-paid
        │   ├── categories.py   # CRUD /categories
        │   ├── dashboard.py    # /dashboard/stats, /popular-books, /active-readers, /monthly-stats
        │   ├── reviews.py      # CRUD /reviews
        │   └── users.py        # CRUD /users, /users/me
        ├── web/                # Web UI routers — SSR Jinja2, cookie-based auth
        │   ├── router.py       # Tập hợp tất cả web sub-routers
        │   ├── auth.py         # GET/POST /login, /register, POST /logout
        │   ├── site.py         # GET / (trang chủ), /books, /books/{id}
        │   ├── dependencies.py # Cookie-based auth — get_current_web_user
        │   ├── templating.py   # render() helper wrapper, flash message read/write
        │   ├── exceptions.py   # WebAuthRequired, WebForbidden — redirect thay vì JSON error
        │   ├── admin/          # /admin/* — yêu cầu Librarian hoặc Admin
        │   │   ├── dashboard.py    # /admin/dashboard
        │   │   ├── books.py        # /admin/books — CRUD, upload ảnh
        │   │   ├── borrowings.py   # /admin/borrowings — issue, return, filter
        │   │   ├── categories.py   # /admin/categories — CRUD inline (HTMX)
        │   │   └── users.py        # /admin/users — quản lý tài khoản
        │   └── reader/         # /reader/* — yêu cầu đăng nhập (Reader+)
        │       ├── borrowings.py   # /reader/my-books, /reader/history
        │       └── profile.py      # /reader/profile, /reader/change-password
        ├── templates/          # Jinja2 HTML templates
        │   ├── base.html       # Layout chính — sidebar responsive + topbar
        │   ├── auth/           # login.html, register.html
        │   ├── site/           # index.html (trang chủ public)
        │   ├── books/          # index.html (danh sách), detail.html (chi tiết + reviews)
        │   ├── admin/          # dashboard, books, borrowings, categories, users
        │   ├── reader/         # my_books, history, profile, change_password
        │   ├── partials/       # HTMX fragments — book_card, pagination, flash message
        │   └── errors/         # 403.html, 404.html
        ├── static/
        │   ├── css/app.css     # Custom CSS bổ sung cho TailwindCSS
        │   ├── js/app.js       # JavaScript helpers
        │   └── uploads/        # Ảnh bìa sách upload — đặt tên theo ISBN
        └── utils/
            └── pagination.py   # Paginator FastAPI dependency + make_paginated_response()
```

**Các class quan trọng:**

| Class | File | Mô tả |
|---|---|---|
| `User` | `models/user.py` | Entity người dùng — UserRole (READER/LIBRARIAN/ADMIN), UserStatus (ACTIVE/INACTIVE), property `is_active` |
| `Book` | `models/book.py` | Entity sách — quản lý tồn kho (quantity / available_quantity), property `is_available` |
| `Category` | `models/category.py` | Thể loại sách |
| `Borrowing` | `models/borrowing.py` | Phiếu mượn — BorrowingStatus, BookCondition, properties `is_overdue` / `days_overdue`, method `calculate_fine()` |
| `Review` | `models/review.py` | Đánh giá sách — unique constraint (user_id, book_id) |
| `BorrowingService` | `services/borrowing.py` | Core circulation logic — issue, return, renew, sync_overdue_statuses |
| `AuthService` | `services/auth.py` | Login, register, refresh token, change password |
| `DashboardService` | `services/dashboard.py` | Tổng hợp KPI, thống kê theo tháng, top sách/độc giả |
| `Settings` | `core/config.py` | Cấu hình hệ thống đọc từ .env, singleton qua `lru_cache` |

---

## 6. Business Logic

### Các luồng nghiệp vụ chính

**1. Quy trình mượn sách (Issue Book)**
```
Thủ thư → Chọn reader + sách → Hệ thống kiểm tra (BorrowingService.issue_book):
  ✓ Reader tồn tại & is_active?
  ✓ Sách tồn tại?
  ✓ book.is_available (status == "Có sẵn" & available_quantity > 0)?
  ✓ Số phiếu mượn active của reader < MAX_ACTIVE_BORROWINGS (5)?
  ✓ Reader chưa đang mượn chính cuốn sách này?
  ✓ due_date (nếu tùy chọn) > borrow_date?
→ Giảm book.available_quantity -= 1
→ Tạo Borrowing record (status=BORROWED, due_date = today + 14 ngày)
```

**2. Quy trình trả sách (Return Book)**
```
Thủ thư → Chọn phiếu mượn → Ghi nhận tình trạng sách (good/fair/poor/damaged)
→ Hệ thống tính: fine = borrowing.calculate_fine(FINE_PER_DAY)
   → fine = days_overdue × 5.000 VND
→ Cập nhật borrowing: status=RETURNED, return_date=today, fine_amount=fine
→ Tăng book.available_quantity += 1
→ Thủ thư ghi nhận thanh toán: mark_fine_paid → fine_paid=True
```

**3. Quy trình gia hạn (Renew)**
```
Reader/Thủ thư → Gia hạn phiếu mượn (BorrowingService.renew_borrowing):
→ Kiểm tra: status == BORROWED
→ Kiểm tra: renewed_count < MAX_RENEWALS (2)
→ due_date += extend_days (mặc định 14 ngày)
→ renewed_count += 1
```

**4. Quy trình đánh giá sách (Review)**
```
Reader → Gửi đánh giá (ReviewService):
→ Kiểm tra: reader đã từng mượn cuốn sách này ít nhất 1 lần
→ Kiểm tra: chưa có review (unique constraint user_id + book_id)
→ Lưu Review — rating 1–5 sao + comment tùy chọn
```

**5. Đồng bộ trạng thái quá hạn (Sync Overdue)**
```
Admin kích hoạt thủ công qua Web UI hoặc REST API
→ BorrowingService.sync_overdue_statuses():
   Tìm tất cả borrowing: status ∈ {BORROWED, OVERDUE} & due_date < today
   → Cập nhật status → OVERDUE
   → Tính lại fine_amount = days_overdue × FINE_PER_DAY
→ Trả về số bản ghi đã cập nhật
```

### Quy tắc nghiệp vụ cốt lõi

| Quy tắc | Giá trị mặc định | Config key (`.env`) |
|---|---|---|
| Thời hạn mượn mặc định | 14 ngày | `BORROWING_PERIOD_DAYS` |
| Số lần gia hạn tối đa | 2 lần | `MAX_RENEWALS` |
| Số phiếu mượn active tối đa mỗi reader | 5 phiếu | `MAX_ACTIVE_BORROWINGS` |
| Phí phạt quá hạn | 5.000 VND/ngày | `FINE_PER_DAY` |
| Xóa sách bị chặn nếu | còn phiếu mượn active | — |
| Xóa user bị chặn ở DB level nếu | còn phiếu mượn (RESTRICT FK) | — |

### Luồng tương tác người dùng

- **Độc giả** có thể duyệt sách, tìm kiếm, xem chi tiết mà **không cần đăng nhập**
- **Độc giả** cần đăng nhập để xem phiếu mượn, gia hạn, và viết đánh giá
- **Thủ thư** quản lý toàn bộ lưu thông sách — cấp phát, trả, theo dõi phí phạt
- **Admin** có toàn quyền, thêm quản lý kho sách, thể loại, người dùng và xem dashboard thống kê

---

## 7. Roles & Permissions

### Vai trò người dùng

| Vai trò | Enum Value | Mô tả |
|---|---|---|
| `reader` | `UserRole.READER` | Độc giả — người dùng cuối |
| `librarian` | `UserRole.LIBRARIAN` | Thủ thư — nhân viên thư viện |
| `admin` | `UserRole.ADMIN` | Quản trị viên — toàn quyền |

### Ma trận phân quyền

| Chức năng | Reader | Librarian | Admin |
|---|---|---|---|
| Duyệt sách (public, không cần đăng nhập) | ✓ | ✓ | ✓ |
| Xem chi tiết sách + reviews | ✓ | ✓ | ✓ |
| Đăng ký tài khoản reader | ✓ | — | — |
| Xem phiếu mượn của bản thân | ✓ | ✓ | ✓ |
| Xem lịch sử mượn của bản thân | ✓ | ✓ | ✓ |
| Gia hạn phiếu mượn của bản thân | ✓ | ✓ | ✓ |
| Viết đánh giá sách (đã từng mượn) | ✓ | ✓ | ✓ |
| Cấp phát sách cho reader | — | ✓ | ✓ |
| Xử lý trả sách | — | ✓ | ✓ |
| Xem tất cả phiếu mượn (toàn hệ thống) | — | ✓ | ✓ |
| Tìm kiếm reader/sách khi cấp phát | — | ✓ | ✓ |
| Xác nhận thanh toán phí phạt | — | ✓ | ✓ |
| Thêm / Sửa sách | — | — | ✓ |
| Xóa sách | — | — | ✓ |
| Quản lý thể loại | — | — | ✓ |
| Quản lý người dùng (role, status, xóa) | — | — | ✓ |
| Xem admin dashboard thống kê | — | — | ✓ |
| Kích hoạt sync trạng thái quá hạn | — | — | ✓ |

### Ràng buộc bảo mật

- Reader chỉ thấy phiếu mượn của bản thân — enforce ở cả API layer và Web layer
- Tài khoản `status=INACTIVE` không thể đăng nhập
- Không thể xóa sách đang có phiếu mượn active (kiểm tra ở service layer)
- Không thể xóa user còn phiếu mượn (RESTRICT foreign key constraint ở DB level)
- Review bị giới hạn 1 review mỗi cặp (user_id, book_id) — unique constraint ở DB level

---

## 8. Main Features

### Nhóm tính năng Public (không cần đăng nhập)
1. **Trang chủ** — Thống kê tổng sách, sách có sẵn, số thể loại; hiển thị sách nổi bật
2. **Duyệt & tìm kiếm sách** — Full-text search (title/author/ISBN), lọc theo thể loại / ngôn ngữ / trạng thái; phân trang
3. **Chi tiết sách** — Thông tin đầy đủ, ảnh bìa, danh sách đánh giá và điểm trung bình sao
4. **Đăng ký tài khoản** — Tạo tài khoản reader mới với validation Pydantic

### Nhóm tính năng Reader (yêu cầu đăng nhập)
5. **Đăng nhập / Đăng xuất** — JWT lưu trong httponly cookie, tự động refresh
6. **Sách đang mượn** — Danh sách phiếu mượn active, trạng thái, số ngày còn lại / quá hạn
7. **Gia hạn sách** — Tự phục vụ (tối đa 2 lần, mỗi lần +14 ngày)
8. **Lịch sử mượn** — Xem toàn bộ lịch sử mượn/trả với phân trang
9. **Hồ sơ cá nhân** — Xem và cập nhật thông tin (họ tên, phone, địa chỉ)
10. **Đổi mật khẩu** — Xác thực mật khẩu hiện tại trước khi cập nhật
11. **Viết đánh giá** — Đánh giá 1–5 sao kèm nhận xét (chỉ được nếu đã mượn sách ít nhất 1 lần)

### Nhóm tính năng Thủ thư (Librarian+)
12. **Cấp phát sách** — Live search reader và sách bằng HTMX (không reload trang), thiết lập ngày trả tùy chọn
13. **Xử lý trả sách** — Ghi nhận tình trạng sách, tự động tính phí phạt theo ngày quá hạn
14. **Quản lý phiếu mượn** — Danh sách toàn bộ phiếu, lọc theo trạng thái / reader / sách / quá hạn
15. **Xác nhận thanh toán phạt** — Đánh dấu fine_paid=True sau khi thu tiền

### Nhóm tính năng Admin
16. **Dashboard thống kê** — KPI cards (tổng sách, users, phiếu mượn, quá hạn, tiền phạt thu/chưa thu); biểu đồ cột Chart.js mượn/trả theo tháng; top 5 sách phổ biến; top 5 độc giả tích cực; bảng tồn kho
17. **Quản lý sách** — CRUD đầy đủ, upload ảnh bìa (lưu theo tên ISBN), lọc/tìm kiếm
18. **Quản lý thể loại** — CRUD inline (HTMX) — thêm/sửa/xóa không cần tải lại trang
19. **Quản lý người dùng** — Danh sách users, thay đổi role, activate/deactivate, xóa tài khoản
20. **Sync trạng thái quá hạn** — Kích hoạt thủ công qua button trên Web UI hoặc API endpoint

### Nhóm tính năng Hệ thống / Developer
21. **REST API đầy đủ** — JSON API tại `/api/v1/` với Swagger UI (`/api/docs`) và ReDoc (`/api/redoc`)
22. **Flash messages** — Thông báo one-shot lưu trong cookie, tự ẩn sau khi hiển thị
23. **Health check** — `GET /health` trả `{"status": "ok", "version": "1.0.0"}`
24. **Live search HTMX** — Partial page update khi tìm kiếm, không full reload
25. **Access log middleware** — Ghi log mọi request với method, path, status code, duration

---

## 9. Database Analysis

### Entities & Attributes

**1. `users` — Người dùng**

| Column | Type | Constraints | Mô tả |
|---|---|---|---|
| id | Integer | PK, INDEX | Khóa chính |
| username | String(255) | UNIQUE, NOT NULL, INDEX | Tên đăng nhập |
| email | String(255) | UNIQUE, NOT NULL, INDEX | Email |
| password_hash | String(255) | NOT NULL | Bcrypt hash — không lưu mật khẩu gốc |
| full_name | String(255) | NOT NULL | Họ tên đầy đủ |
| phone | String(20) | NULL | Số điện thoại |
| address | String(500) | NULL | Địa chỉ |
| role | Enum | NOT NULL, DEFAULT=reader | reader / librarian / admin |
| status | Enum(int) | NOT NULL, DEFAULT=10 | 0=inactive / 10=active |
| created_at | DateTime(tz) | NOT NULL | Thời điểm tạo (UTC) |
| updated_at | DateTime(tz) | NOT NULL | Thời điểm cập nhật (UTC) |

**2. `categories` — Thể loại sách**

| Column | Type | Constraints | Mô tả |
|---|---|---|---|
| id | Integer | PK | Khóa chính |
| name | String(100) | UNIQUE, NOT NULL | Tên thể loại |
| description | Text | NULL | Mô tả |
| created_at | DateTime(tz) | NOT NULL | Thời điểm tạo |

**3. `books` — Sách**

| Column | Type | Constraints | Mô tả |
|---|---|---|---|
| id | Integer | PK, INDEX | Khóa chính |
| title | String(255) | NOT NULL, INDEX | Tựa sách |
| author | String(255) | NOT NULL, INDEX | Tác giả |
| isbn | String(20) | UNIQUE, NULL, INDEX | Mã ISBN — dùng làm tên file ảnh bìa |
| publisher | String(255) | NULL | Nhà xuất bản |
| publication_year | SmallInteger | NULL | Năm xuất bản |
| language | Enum | NOT NULL, DEFAULT=vi | vi / en |
| description | Text | NULL | Mô tả nội dung |
| cover_image | String(255) | NULL | Đường dẫn ảnh bìa |
| quantity | Integer | NOT NULL, DEFAULT=1 | Tổng số bản sách |
| available_quantity | Integer | NOT NULL, DEFAULT=1 | Số bản hiện có sẵn để mượn |
| status | Enum | NOT NULL, DEFAULT=Có sẵn | Có sẵn / Hư hỏng / Mất |
| category_id | Integer | FK→categories(SET NULL) | Thể loại — NULL nếu thể loại bị xóa |
| created_at | DateTime(tz) | NOT NULL | Thời điểm tạo |
| updated_at | DateTime(tz) | NOT NULL | Thời điểm cập nhật |

**4. `borrowings` — Phiếu mượn**

| Column | Type | Constraints | Mô tả |
|---|---|---|---|
| id | Integer | PK | Khóa chính |
| user_id | Integer | FK→users(RESTRICT), INDEX | Reader mượn sách |
| book_id | Integer | FK→books(RESTRICT), INDEX | Sách được mượn |
| borrow_date | Date | NOT NULL | Ngày mượn |
| due_date | Date | NOT NULL | Hạn trả (borrow_date + 14 ngày mặc định) |
| return_date | Date | NULL | Ngày thực tế trả — NULL khi chưa trả |
| status | Enum | NOT NULL, INDEX | borrowed / returned / overdue |
| book_condition | Enum | NULL | good / fair / poor / damaged — ghi lúc trả |
| renewed_count | Integer | NOT NULL, DEFAULT=0 | Số lần đã gia hạn (max 2) |
| fine_amount | Float | NOT NULL, DEFAULT=0 | Tiền phạt tính theo ngày (VND) |
| fine_paid | Boolean | NOT NULL, DEFAULT=false | Đã thanh toán phạt chưa |
| librarian_notes | Text | NULL | Ghi chú của thủ thư khi xử lý |
| created_at | DateTime(tz) | NOT NULL | Thời điểm tạo |
| updated_at | DateTime(tz) | NOT NULL | Thời điểm cập nhật |

**5. `reviews` — Đánh giá sách**

| Column | Type | Constraints | Mô tả |
|---|---|---|---|
| id | Integer | PK | Khóa chính |
| book_id | Integer | FK→books(CASCADE), INDEX | Sách được đánh giá |
| user_id | Integer | FK→users(CASCADE), INDEX | Reader đánh giá |
| rating | SmallInteger | NOT NULL | Điểm đánh giá (1–5) |
| comment | Text | NULL | Nhận xét tự do |
| status | Enum(int) | NOT NULL, DEFAULT=1 | 0=hidden / 1=active |
| created_at | DateTime(tz) | NOT NULL | Thời điểm tạo |
| updated_at | DateTime(tz) | NOT NULL | Thời điểm cập nhật |

Unique constraint: `(user_id, book_id)` — mỗi reader chỉ được review 1 lần mỗi cuốn sách

### Relationships

```
categories (1) ─────────────── (0..N) books
                                        │
                              ┌─────────┴──────────┐
                              │                    │
users (1) ──────── (0..N) borrowings           reviews (0..N) ──── (1) users
                              │
                          books (1) ───── (0..N) borrowings
                          books (1) ───── (0..N) reviews
```

| Quan hệ | Kiểu | ON DELETE | Ý nghĩa |
|---|---|---|---|
| Category → Books | One-to-Many | SET NULL | Xóa thể loại → sách vẫn tồn tại, category_id = NULL |
| User → Borrowings | One-to-Many | RESTRICT | Không xóa user còn phiếu mượn |
| Book → Borrowings | One-to-Many | RESTRICT | Không xóa sách còn phiếu mượn |
| User → Reviews | One-to-Many | CASCADE | Xóa user → xóa toàn bộ reviews của user đó |
| Book → Reviews | One-to-Many | CASCADE | Xóa sách → xóa toàn bộ reviews của sách đó |

### Ghi chú thiết kế database

- **Database engine:** SQLite (file `backend/library.db`) — phù hợp cho đồ án và môi trường đơn server
- **ORM driver:** SQLAlchemy 2.x async với aiosqlite — truy vấn non-blocking
- **Migration:** Alembic quản lý phiên bản schema (`001_initial_schema.py`)
- **Dev mode:** Bảng tự động tạo khi khởi động (`ENVIRONMENT=development`) — không cần chạy migration thủ công
- **Custom SQLite function:** `normalize_vi()` đăng ký qua SQLAlchemy event để hỗ trợ tìm kiếm tiếng Việt có dấu
- **Timestamp:** Tất cả bảng dùng `DateTime(timezone=True)` với giá trị UTC

---

## 10. Presentation-Relevant Information

### Luồng nghiệp vụ (phù hợp trình bày)

1. **Luồng mượn sách:** Thủ thư live-search reader → live-search sách → hệ thống kiểm tra 5 điều kiện → tạo phiếu → giảm tồn kho
2. **Luồng trả sách:** Thủ thư chọn phiếu → ghi tình trạng → hệ thống tự tính phạt theo ngày → cập nhật tồn kho → ghi nhận thu phạt
3. **Luồng độc giả tự phục vụ:** Tìm sách (public) → đăng ký → xem phiếu mượn → gia hạn → đánh giá sách

### Kiến trúc hệ thống (phù hợp trình bày)

- Kiến trúc **Monolith Full-stack** — 1 server FastAPI phục vụ cả Web UI (SSR) và REST API
- **Pattern 4 tầng:** API/Web Layer → Service Layer → Repository Layer → Database
- **Dual authentication:** JWT Bearer token cho REST API; httponly cookie cho Web UI
- **RBAC 3 cấp:** Reader < Librarian < Admin — enforce ở cả API dependency và Web route

### Công nghệ (phù hợp trình bày)

- **Backend:** Python 3.12 + FastAPI — modern, async, hiệu năng cao, auto-generate docs
- **Database:** SQLite + SQLAlchemy async ORM — nhẹ, không cần cài đặt server riêng
- **Frontend:** Jinja2 SSR + HTMX (partial update) + Alpine.js (reactivity nhẹ)
- **Auth:** JWT (PyJWT) + bcrypt — chuẩn công nghiệp
- **UI:** TailwindCSS utility-first + Chart.js biểu đồ

### Điểm nổi bật kỹ thuật (phù hợp trình bày)

- **Live search không cần reload** — HTMX gửi partial HTTP request, server trả HTML fragment
- **Tự động tính phí phạt** — method `calculate_fine()` trên ORM model, tích hợp vào cả return flow và sync_overdue
- **Dashboard động** — Chart.js render biểu đồ từ dữ liệu JSON API, top sách và reader theo aggregation SQL
- **REST API tự động document** — FastAPI + Pydantic v2 sinh Swagger UI tại `/api/docs`
- **Upload ảnh bìa async** — aiofiles xử lý file I/O không blocking, đặt tên file theo ISBN

### Tương tác người dùng theo vai trò

- **Độc giả:** Duyệt (public) → Đăng ký → Đăng nhập → Xem phiếu mượn → Gia hạn → Đánh giá
- **Thủ thư:** Đăng nhập → Live search cấp phát → Xử lý trả → Theo dõi phiếu → Xác nhận thu phạt
- **Admin:** Dashboard → Quản lý kho sách → Quản lý thể loại → Quản lý người dùng → Sync quá hạn
