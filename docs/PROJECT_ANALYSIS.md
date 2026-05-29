# PROJECT_ANALYSIS.md — Library Management System

---

## 1. Project Overview

**Project name:** Library Management System (LMS)

**Project purpose:**
Hệ thống quản lý thư viện trực tuyến, cho phép độc giả duyệt và mượn sách, thủ thư xử lý phiếu mượn/trả, và quản trị viên quản lý toàn bộ kho sách, người dùng và theo dõi hiệu quả hoạt động qua dashboard thống kê.

**Target users:**
- **Độc giả (Reader):** Người dùng cuối muốn mượn sách từ thư viện
- **Thủ thư (Librarian):** Nhân viên thư viện xử lý lưu thông sách (mượn/trả)
- **Quản trị viên (Admin):** Quản lý toàn bộ hệ thống — kho sách, thể loại, người dùng, báo cáo

**Main objectives:**
- Số hoá quy trình mượn/trả sách, thay thế sổ sách giấy
- Kiểm soát tồn kho sách theo thời gian thực
- Tự động tính phí phạt khi trả sách trễ
- Cung cấp thống kê hoạt động cho ban quản lý thư viện
- Cho phép độc giả tìm kiếm và đánh giá sách trực tuyến

---

## 2. Business Context

**Problem statement:**
Thư viện truyền thống quản lý sách và phiếu mượn thủ công bằng giấy tờ, dẫn đến khó kiểm soát tồn kho, dễ thất thoát thông tin, không có báo cáo tổng hợp tức thời, và khó theo dõi sách quá hạn.

**Why the system exists:**
Dự án được xây dựng lại từ một hệ thống PHP/Yii2 cũ, chuyển sang nền tảng Python/FastAPI hiện đại hơn, nhằm:
- Cải thiện hiệu năng và khả năng bảo trì của mã nguồn
- Cung cấp REST API để dễ tích hợp sau này
- Nâng cao trải nghiệm người dùng với giao diện web phản hồi nhanh (HTMX, Alpine.js)

**Expected benefits:**
- Giảm thời gian xử lý mượn/trả sách
- Loại bỏ lỗi thủ công trong quản lý tồn kho
- Tự động hóa tính phí phạt sách trễ
- Cung cấp số liệu thống kê trực quan cho ban quản lý

---

## 3. System Overview

**High level architecture:**

Hệ thống theo kiến trúc **Monolith Full-stack**, chạy trên một server FastAPI duy nhất phục vụ cả hai giao diện:

```
[Trình duyệt Web]
      │
      ├─ Web UI (HTML/Jinja2 + HTMX + Alpine.js)
      │       └─ /web/* routes (Server-Side Rendering)
      │
      └─ REST API (JSON)
              └─ /api/v1/* routes
                        │
                 [FastAPI Application]
                        │
              ┌─────────┴─────────┐
         [Services]          [Repositories]
              │                    │
         [Models/ORM]       [SQLAlchemy Async]
              │
         [SQLite DB — library.db]
```

**Main modules:**

| Module | Đường dẫn | Trách nhiệm |
|---|---|---|
| API v1 | `app/api/v1/` | REST JSON API endpoints |
| Web UI | `app/web/` | Server-rendered HTML pages |
| Services | `app/services/` | Business logic |
| Repositories | `app/repositories/` | Database queries |
| Models | `app/models/` | SQLAlchemy ORM entities |
| Schemas | `app/schemas/` | Pydantic validation & serialization |
| Core | `app/core/` | Config, Security (JWT, bcrypt) |
| Middleware | `app/middleware/` | Request logging |
| Templates | `app/templates/` | Jinja2 HTML templates |

**Module responsibilities:**

- **Services:** Toàn bộ business logic — kiểm tra quy tắc nghiệp vụ trước khi thực hiện thao tác DB
- **Repositories:** Truy vấn database thuần túy, không có logic nghiệp vụ
- **API v1:** Tiếp nhận HTTP request, gọi service, trả JSON response
- **Web:** Tiếp nhận HTTP request, gọi service, render HTML template
- **Dependencies:** Dependency injection — xác thực JWT (API) và cookie (Web), kiểm tra role (RBAC)

---

## 4. Technology Stack

### Programming Language
| Technology | Version | Purpose |
|---|---|---|
| **Python** | 3.12+ | Ngôn ngữ lập trình chính của toàn bộ backend |

### Frameworks & Runtime
| Technology | Version | Purpose |
|---|---|---|
| **FastAPI** | ≥0.111.0 | Web framework bất đồng bộ (async), xây dựng REST API và Web UI |
| **Uvicorn** | ≥0.29.0 | ASGI server để chạy ứng dụng FastAPI |

### Database & ORM
| Technology | Version | Purpose |
|---|---|---|
| **SQLite** | Built-in | Cơ sở dữ liệu quan hệ nhẹ, lưu trữ tất cả dữ liệu trong file `library.db` |
| **SQLAlchemy** | ≥2.0.30 | ORM bất đồng bộ (async), ánh xạ Python objects ↔ bảng DB |
| **aiosqlite** | ≥0.20.0 | Driver async cho SQLite |
| **Alembic** | ≥1.13.1 | Migration schema cơ sở dữ liệu |

### Authentication & Security
| Technology | Version | Purpose |
|---|---|---|
| **PyJWT** | ≥2.8.0 | Tạo và xác thực JSON Web Token (JWT) — access token & refresh token |
| **bcrypt** | ≥4.0.0 | Hash mật khẩu người dùng (thay thế passlib đã ngừng phát triển) |
| **itsdangerous** | ≥2.1.2 | Ký và xác thực cookie flash message |

### Validation & Settings
| Technology | Version | Purpose |
|---|---|---|
| **Pydantic v2** | ≥2.8.0 | Schema validation, serialization cho API request/response |
| **pydantic-settings** | ≥2.3.0 | Đọc cấu hình từ file `.env` |
| **email-validator** | ≥2.1.1 | Xác thực định dạng email |

### Templating & UI
| Technology | Version | Purpose |
|---|---|---|
| **Jinja2** | ≥3.1.4 | Template engine — render HTML phía server (SSR) |
| **HTMX** | 1.9.12 (CDN) | Xử lý partial page update (live search, dynamic table rows) không cần JavaScript thuần |
| **Alpine.js** | 3.x (CDN) | Reactivity nhẹ phía client (dropdown, sidebar toggle) |
| **TailwindCSS** | CDN Play (JIT) | CSS utility-first — styling toàn bộ giao diện |
| **Chart.js** | 4 (CDN) | Vẽ biểu đồ thống kê trên admin dashboard |
| **python-multipart** | ≥0.0.9 | Parse form data & file upload |
| **aiofiles** | ≥23.2.1 | Xử lý file I/O bất đồng bộ (ảnh bìa sách) |

### Testing & Dev Tools
| Technology | Version | Purpose |
|---|---|---|
| **pytest** | ≥8.2.0 | Framework kiểm thử đơn vị và tích hợp |
| **pytest-asyncio** | ≥0.23.6 | Hỗ trợ test async functions |
| **httpx** | ≥0.27.0 | HTTP client bất đồng bộ cho integration tests |
| **Ruff** | ≥0.4.4 | Linting và formatting code Python |

---

## 5. Project Structure

```
Python_LibraryManagement/
├── .env                        # Biến môi trường (SECRET_KEY, DB URL, v.v.)
├── .env.example                # Template hướng dẫn cấu hình
├── requirements.txt            # Danh sách dependencies Python
├── README.md                   # Tài liệu dự án
├── docs/                       # Tài liệu phân tích & trình bày
└── backend/
    ├── alembic.ini             # Cấu hình Alembic
    ├── pytest.ini              # Cấu hình pytest
    ├── seed.py                 # Script tạo dữ liệu mẫu
    ├── library.db              # File SQLite database
    ├── alembic/
    │   └── versions/
    │       └── 001_initial_schema.py  # Migration khởi tạo schema DB
    ├── tests/
    │   ├── conftest.py         # Fixtures dùng chung cho tests
    │   ├── test_auth.py        # Test đăng ký, đăng nhập, JWT
    │   ├── test_books.py       # Test CRUD sách, phân quyền
    │   └── test_borrowings.py  # Test mượn/trả, gia hạn, phạt
    └── app/
        ├── main.py             # App factory, lifespan, middleware setup
        ├── core/
        │   ├── config.py       # Settings (pydantic-settings, đọc .env)
        │   └── security.py     # JWT helpers, bcrypt hash/verify
        ├── db/
        │   ├── base.py         # DeclarativeBase SQLAlchemy
        │   └── session.py      # Async engine, session factory, get_db()
        ├── models/             # SQLAlchemy ORM models (5 entity)
        │   ├── user.py
        │   ├── book.py
        │   ├── category.py
        │   ├── borrowing.py
        │   └── review.py
        ├── schemas/            # Pydantic v2 schemas (request/response)
        │   ├── auth.py
        │   ├── book.py
        │   ├── borrowing.py
        │   ├── category.py
        │   ├── dashboard.py
        │   ├── review.py
        │   ├── user.py
        │   └── common.py       # PaginatedResponse, MessageResponse
        ├── repositories/       # Data access layer (async DB queries)
        │   ├── book.py
        │   ├── borrowing.py
        │   ├── category.py
        │   ├── review.py
        │   └── user.py
        ├── services/           # Business logic layer
        │   ├── auth.py         # Login, register, refresh token
        │   ├── book.py         # CRUD sách, kiểm tra tồn kho
        │   ├── borrowing.py    # Mượn/trả/gia hạn/phạt
        │   ├── category.py     # CRUD thể loại
        │   ├── dashboard.py    # Thống kê KPI, biểu đồ
        │   ├── review.py       # Đánh giá sách
        │   └── user.py         # Quản lý người dùng
        ├── dependencies/
        │   ├── auth.py         # get_current_user (Bearer token)
        │   └── rbac.py         # require_reader/librarian/admin
        ├── middleware/
        │   └── logging.py      # Access log middleware
        ├── api/v1/             # REST API routers (/api/v1/...)
        │   ├── router.py
        │   ├── auth.py
        │   ├── books.py
        │   ├── borrowings.py
        │   ├── categories.py
        │   ├── dashboard.py
        │   ├── reviews.py
        │   └── users.py
        ├── web/                # Web UI routers (SSR Jinja2)
        │   ├── router.py       # Tập hợp tất cả web sub-routers
        │   ├── auth.py         # /login, /register, /logout
        │   ├── site.py         # /, /books, /books/{id}
        │   ├── dependencies.py # Cookie-based auth (web)
        │   ├── templating.py   # render() helper, flash message
        │   ├── exceptions.py   # WebAuthRequired, WebForbidden
        │   ├── admin/          # /admin/* — quản trị
        │   │   ├── dashboard.py
        │   │   ├── books.py
        │   │   ├── borrowings.py
        │   │   ├── categories.py
        │   │   └── users.py
        │   └── reader/         # /reader/* — độc giả
        │       ├── borrowings.py
        │       └── profile.py
        ├── templates/          # Jinja2 HTML templates
        │   ├── base.html       # Layout chính (sidebar + topbar)
        │   ├── auth/           # login.html, register.html
        │   ├── site/           # index.html (trang chủ)
        │   ├── books/          # index.html, detail.html
        │   ├── admin/          # dashboard, books, borrowings, categories, users
        │   ├── reader/         # my_books, history, profile, change_password
        │   ├── partials/       # HTMX fragments (book_card, pagination, flash)
        │   └── errors/         # 403.html, 404.html
        ├── static/
        │   ├── css/app.css
        │   ├── js/app.js
        │   └── uploads/        # Ảnh bìa sách upload (đặt tên theo ISBN)
        └── utils/
            └── pagination.py   # Paginator helper
```

**Main classes:**

| Class | File | Mô tả |
|---|---|---|
| `User` | `models/user.py` | Entity người dùng, có role READER/LIBRARIAN/ADMIN |
| `Book` | `models/book.py` | Entity sách với tồn kho (quantity/available_quantity) |
| `Category` | `models/category.py` | Thể loại sách |
| `Borrowing` | `models/borrowing.py` | Phiếu mượn, chứa fine_amount, renewed_count |
| `Review` | `models/review.py` | Đánh giá sách (1 review/user/book) |
| `BorrowingService` | `services/borrowing.py` | Core circulation logic — issue, return, renew, fine |
| `AuthService` | `services/auth.py` | Login, register, JWT token management |
| `DashboardService` | `services/dashboard.py` | Tổng hợp KPI, thống kê tháng, top sách/độc giả |
| `Settings` | `core/config.py` | Cấu hình hệ thống đọc từ .env |

---

## 6. Business Logic

### Main Workflows

**1. Quy trình mượn sách (Issue Book)**
```
Thủ thư → Chọn reader + sách → Hệ thống kiểm tra:
  ✓ Reader tồn tại & active?
  ✓ Sách tồn tại?
  ✓ available_quantity > 0 & status == "Có sẵn"?
  ✓ Reader chưa đạt giới hạn 5 phiếu mượn đang active?
  ✓ Reader chưa đang mượn chính cuốn sách này?
→ Tạo Borrowing record
→ Giảm book.available_quantity -= 1
→ Mặc định hạn trả = ngày mượn + 14 ngày
```

**2. Quy trình trả sách (Return Book)**
```
Thủ thư → Chọn phiếu mượn → Ghi nhận tình trạng sách (good/fair/poor/damaged)
→ Hệ thống tính phí phạt = days_overdue × 5,000 VND
→ Cập nhật borrowing: status=RETURNED, return_date=today, fine_amount
→ Tăng book.available_quantity += 1
→ Thủ thư xác nhận thanh toán tiền phạt (mark_fine_paid)
```

**3. Quy trình gia hạn (Renew)**
```
Reader/Thủ thư → Gia hạn phiếu mượn
→ Kiểm tra: status == BORROWED & renewed_count < 2
→ due_date += 14 ngày; renewed_count += 1
```

**4. Quy trình đánh giá sách (Review)**
```
Reader → Phải đã mượn sách ít nhất 1 lần
→ Mỗi reader chỉ được 1 review/sách (unique constraint)
→ Rating 1–5 sao + comment tuỳ chọn
```

**5. Quy trình đồng bộ sách quá hạn (Sync Overdue)**
```
Admin kích hoạt thủ công (hoặc cron job)
→ Tìm tất cả borrowing: status=BORROWED & due_date < today
→ Cập nhật status → OVERDUE
→ Tính lại fine_amount = days_overdue × fine_per_day
```

### Core Business Rules

| Rule | Giá trị mặc định | Config key |
|---|---|---|
| Thời hạn mượn | 14 ngày | `BORROWING_PERIOD_DAYS` |
| Tối đa gia hạn | 2 lần | `MAX_RENEWALS` |
| Tối đa phiếu mượn đang active | 5 phiếu/reader | `MAX_ACTIVE_BORROWINGS` |
| Phí phạt quá hạn | 5,000 VND/ngày | `FINE_PER_DAY` |
| Xóa sách | Bị chặn nếu còn phiếu mượn active | — |

### Key Interactions

- **Độc giả** có thể duyệt sách và xem chi tiết mà không cần đăng nhập
- **Độc giả** cần đăng nhập để xem sách đang mượn, lịch sử, gia hạn
- **Thủ thư** quản lý toàn bộ luồng mượn/trả sách
- **Admin** có toàn quyền, thêm quản lý sách, thể loại, người dùng và xem dashboard

---

## 7. Roles & Permissions

### User Roles

| Role | Mã số | Mô tả |
|---|---|---|
| `reader` | Reader | Độc giả — người dùng cuối |
| `librarian` | Librarian | Thủ thư — nhân viên thư viện |
| `admin` | Admin | Quản trị viên — toàn quyền |

### Permission Matrix

| Chức năng | Reader | Librarian | Admin |
|---|---|---|---|
| Duyệt sách (public) | ✓ | ✓ | ✓ |
| Xem chi tiết sách + reviews | ✓ | ✓ | ✓ |
| Đăng ký tài khoản | ✓ | — | — |
| Xem sách đang mượn của mình | ✓ | ✓ | ✓ |
| Xem lịch sử mượn của mình | ✓ | ✓ | ✓ |
| Gia hạn phiếu mượn của mình | ✓ | ✓ | ✓ |
| Viết đánh giá sách | ✓ | ✓ | ✓ |
| Cấp phát sách cho reader | — | ✓ | ✓ |
| Xử lý trả sách | — | ✓ | ✓ |
| Xem tất cả phiếu mượn | — | ✓ | ✓ |
| Tìm kiếm user/sách khi cấp phát | — | ✓ | ✓ |
| Thêm/Sửa sách | — | — | ✓ |
| Xóa sách | — | — | ✓ |
| Quản lý thể loại | — | — | ✓ |
| Quản lý người dùng (role, status) | — | — | ✓ |
| Xem admin dashboard | — | — | ✓ |
| Kích hoạt sync overdue | — | — | ✓ |

### Restrictions

- Reader chỉ thấy phiếu mượn của bản thân (API và Web đều enforce)
- Tài khoản bị inactive không thể đăng nhập
- Không thể xóa sách có phiếu mượn đang active
- Không thể xóa user có phiếu mượn (RESTRICT constraint)
- Review bị giới hạn 1 review mỗi cặp (user, book)

---

## 8. Main Features

### Nhóm tính năng công khai (Public)
1. **Trang chủ** — Hiển thị thống kê tổng sách, sách có sẵn, số thể loại; sách nổi bật
2. **Duyệt sách** — Tìm kiếm full-text (title/author/ISBN), lọc theo thể loại, ngôn ngữ, trạng thái; phân trang
3. **Chi tiết sách** — Thông tin đầy đủ, ảnh bìa, danh sách đánh giá và điểm trung bình
4. **Đăng ký tài khoản** — Tạo tài khoản reader mới

### Nhóm tính năng Reader
5. **Đăng nhập / Đăng xuất** — JWT lưu trong httponly cookie
6. **Sách đang mượn** — Danh sách phiếu mượn đang active, trạng thái, hạn trả
7. **Gia hạn sách** — Gia hạn tự phục vụ (tối đa 2 lần)
8. **Lịch sử mượn** — Xem toàn bộ lịch sử mượn/trả
9. **Hồ sơ cá nhân** — Xem và cập nhật thông tin cá nhân
10. **Đổi mật khẩu** — Xác thực mật khẩu hiện tại trước khi đổi
11. **Viết đánh giá** — Đánh giá 1–5 sao kèm nhận xét (cần đã mượn sách)

### Nhóm tính năng Thủ thư
12. **Cấp phát sách** — Tìm kiếm live (HTMX) reader và sách, thiết lập ngày trả
13. **Xử lý trả sách** — Ghi nhận tình trạng sách, tự động tính phí phạt
14. **Quản lý phiếu mượn** — Xem tất cả phiếu, lọc theo trạng thái/reader/sách/quá hạn
15. **Xác nhận thanh toán phạt** — Đánh dấu tiền phạt đã thu

### Nhóm tính năng Admin
16. **Dashboard thống kê** — KPI cards (tổng sách, users, phiếu mượn, phiếu quá hạn, tiền phạt); biểu đồ cột Chart.js số lượng mượn/trả theo tháng; top 5 sách/độc giả; danh sách tồn kho
17. **Quản lý sách** — CRUD đầy đủ, upload ảnh bìa, lọc/tìm kiếm
18. **Quản lý thể loại** — CRUD inline (HTMX), không cần tải lại trang
19. **Quản lý người dùng** — Xem danh sách, thay đổi role, activate/deactivate, xóa
20. **Sync trạng thái quá hạn** — Kích hoạt thủ công hoặc qua API endpoint

### Nhóm tính năng Hệ thống / Developer
21. **REST API** — Full JSON API tại `/api/v1/` với Swagger UI, ReDoc
22. **Flash messages** — Thông báo one-shot tự ẩn sau thao tác
23. **Health check** — `GET /health`
24. **Live search** — HTMX partial update khi tìm kiếm (không full reload)

---

## 9. Database Analysis

### Entities & Attributes

**1. `users` — Người dùng**

| Column | Type | Constraints | Mô tả |
|---|---|---|---|
| id | Integer | PK | Khóa chính |
| username | String(255) | UNIQUE, NOT NULL, INDEX | Tên đăng nhập |
| email | String(255) | UNIQUE, NOT NULL, INDEX | Email |
| password_hash | String(255) | NOT NULL | Bcrypt hash |
| full_name | String(255) | NOT NULL | Họ tên đầy đủ |
| phone | String(20) | NULL | Số điện thoại |
| address | String(500) | NULL | Địa chỉ |
| role | Enum | NOT NULL, DEFAULT=reader | reader / librarian / admin |
| status | Enum | NOT NULL, DEFAULT=10 (active) | 0=inactive / 10=active |
| created_at | DateTime(tz) | NOT NULL | Thời điểm tạo |
| updated_at | DateTime(tz) | NOT NULL | Thời điểm cập nhật |

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
| id | Integer | PK | Khóa chính |
| title | String(255) | NOT NULL, INDEX | Tựa sách |
| author | String(255) | NOT NULL, INDEX | Tác giả |
| isbn | String(20) | UNIQUE, NULL, INDEX | Mã ISBN |
| publisher | String(255) | NULL | Nhà xuất bản |
| publication_year | SmallInteger | NULL | Năm xuất bản |
| language | Enum | NOT NULL, DEFAULT=vi | vi / en |
| description | Text | NULL | Mô tả nội dung |
| cover_image | String(255) | NULL | Đường dẫn ảnh bìa |
| quantity | Integer | NOT NULL, DEFAULT=1 | Tổng số bản |
| available_quantity | Integer | NOT NULL, DEFAULT=1 | Số bản hiện có sẵn |
| status | Enum | NOT NULL, DEFAULT=Có sẵn | Có sẵn / Hư hỏng / Mất |
| category_id | Integer | FK→categories(SET NULL) | Thể loại |
| created_at | DateTime(tz) | NOT NULL | Thời điểm tạo |
| updated_at | DateTime(tz) | NOT NULL | Thời điểm cập nhật |

**4. `borrowings` — Phiếu mượn**

| Column | Type | Constraints | Mô tả |
|---|---|---|---|
| id | Integer | PK | Khóa chính |
| user_id | Integer | FK→users(RESTRICT), INDEX | Reader mượn sách |
| book_id | Integer | FK→books(RESTRICT), INDEX | Sách được mượn |
| borrow_date | Date | NOT NULL | Ngày mượn |
| due_date | Date | NOT NULL | Hạn trả |
| return_date | Date | NULL | Ngày thực tế trả |
| status | Enum | NOT NULL, INDEX | borrowed / returned / overdue |
| book_condition | Enum | NULL | good / fair / poor / damaged |
| renewed_count | Integer | NOT NULL, DEFAULT=0 | Số lần đã gia hạn |
| fine_amount | Float | NOT NULL, DEFAULT=0 | Tiền phạt (VND) |
| fine_paid | Boolean | NOT NULL, DEFAULT=false | Đã thanh toán phạt chưa |
| librarian_notes | Text | NULL | Ghi chú của thủ thư |
| created_at | DateTime(tz) | NOT NULL | Thời điểm tạo |
| updated_at | DateTime(tz) | NOT NULL | Thời điểm cập nhật |

**5. `reviews` — Đánh giá sách**

| Column | Type | Constraints | Mô tả |
|---|---|---|---|
| id | Integer | PK | Khóa chính |
| book_id | Integer | FK→books(CASCADE), INDEX | Sách được đánh giá |
| user_id | Integer | FK→users(CASCADE), INDEX | Reader đánh giá |
| rating | SmallInteger | NOT NULL | Điểm đánh giá (1–5) |
| comment | Text | NULL | Nhận xét |
| status | Enum | NOT NULL, DEFAULT=1 (active) | 0=hidden / 1=active |
| created_at | DateTime(tz) | NOT NULL | Thời điểm tạo |
| updated_at | DateTime(tz) | NOT NULL | Thời điểm cập nhật |

Unique constraint: `(user_id, book_id)` — mỗi user chỉ được review 1 lần/sách

### Relationships

```
categories (1) ──── (0..N) books
                              │
                    ┌─────────┤─────────┐
                    │                   │
users (1) ── (0..N) borrowings       reviews (0..N) ── (1) users
                    │
                books (1) ── (0..N) borrowings
                books (1) ── (0..N) reviews
```

Chi tiết:
- **Category → Books:** One-to-Many, ON DELETE SET NULL (sách không bị xóa khi xóa thể loại)
- **User → Borrowings:** One-to-Many, ON DELETE RESTRICT (không xóa user còn phiếu mượn)
- **Book → Borrowings:** One-to-Many, ON DELETE RESTRICT (không xóa sách còn phiếu mượn)
- **User → Reviews:** One-to-Many, ON DELETE CASCADE (xóa user → xóa reviews)
- **Book → Reviews:** One-to-Many, ON DELETE CASCADE (xóa sách → xóa reviews)

### Database Structure Notes

- Database: **SQLite** (file `backend/library.db`)
- Engine: **SQLAlchemy async** với driver `aiosqlite`
- Migration tool: **Alembic** (1 migration file: `001_initial_schema.py`)
- Trong development mode, bảng tự động tạo khi khởi động app (không cần chạy migration thủ công)
- ISBN được dùng làm tên file ảnh bìa sách

---

## 10. Presentation-Relevant Information

### Business Flow (phù hợp để trình bày)

1. **Luồng mượn sách:** Thủ thư tìm reader → tìm sách → kiểm tra điều kiện → tạo phiếu → cập nhật tồn kho
2. **Luồng trả sách:** Thủ thư chọn phiếu → ghi tình trạng → tính phạt tự động → cập nhật tồn kho → thu phạt
3. **Luồng độc giả tự phục vụ:** Tìm sách → xem chi tiết → đăng ký → mượn (qua thủ thư) → gia hạn → đánh giá

### System Architecture (phù hợp để trình bày)

- Kiến trúc Monolith — 1 server FastAPI phục vụ cả Web UI và REST API
- Pattern 3 tầng: API/Web layer → Service layer → Repository layer → Database
- Authentication kép: JWT Bearer token (API) & httponly cookie (Web)
- RBAC 3 cấp: reader < librarian < admin

### Technologies (phù hợp để trình bày)

- **Backend:** Python + FastAPI (modern, async, high performance)
- **Database:** SQLite + SQLAlchemy async ORM
- **Frontend:** Server-side rendering Jinja2 + HTMX (partial updates không cần SPA)
- **Auth:** JWT + bcrypt (industry standard)
- **UI:** TailwindCSS + Alpine.js (modern, responsive)

### Features (phù hợp để trình bày)

- Live search không cần reload (HTMX)
- Tự động tính phí phạt theo ngày
- Dashboard với biểu đồ Chart.js
- REST API đầy đủ với Swagger UI
- Upload ảnh bìa sách

### User Interactions (phù hợp để trình bày)

- **Độc giả:** Duyệt → Tìm kiếm → Đăng ký → Xem phiếu mượn → Gia hạn → Đánh giá
- **Thủ thư:** Đăng nhập → Cấp phát sách (live search) → Xử lý trả → Theo dõi phiếu
- **Admin:** Dashboard → Quản lý kho sách → Quản lý người dùng → Báo cáo thống kê
