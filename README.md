# Hệ Thống Quản Lý Thư Viện

Hệ thống quản lý thư viện trực tuyến full-stack xây dựng bằng **Python / FastAPI**, render giao diện phía server với **Jinja2 + HTMX + Alpine.js + TailwindCSS**.

---

## Mục Lục

- [Tính Năng](#tính-năng)
- [Tech Stack](#tech-stack)
- [Cấu Trúc Dự Án](#cấu-trúc-dự-án)
- [Cài đặt & Chạy Ứng Dụng](#cài-đặt--chạy-ứng-dụng)
- [Biến Môi Trường](#biến-môi-trường)
- [Cơ Sở Dữ Liệu & Migration](#cơ-sở-dữ-liệu--migration)
- [Seed Dữ Liệu Mẫu](#seed-dữ-liệu-mẫu)
- [Chạy Ứng Dụng](#chạy-ứng-dụng)
- [Danh Sách URL](#danh-sách-url)
- [API Reference](#api-reference)
- [Chạy Tests](#chạy-tests)
- [Phân Quyền](#phân-quyền)
- [Quy Tắc Nghiệp Vụ](#quy-tắc-nghiệp-vụ)

---

## Tính Năng

- **Kho sách** — duyệt, tìm kiếm, lọc theo thể loại / ngôn ngữ / trạng thái
- **Luồng mượn sách** — cấp phát, trả, gia hạn, theo dõi quá hạn, tính phí phạt tự động
- **Phân quyền theo vai trò** — Độc giả (Reader), Thủ thư (Librarian), Quản trị viên (Admin)
- **Xác thực JWT** — httponly cookie cho Web UI, Bearer token cho REST API
- **Dashboard quản trị** — KPI cards, biểu đồ mượn/trả theo tháng (Chart.js), top sách/độc giả
- **Đánh giá sách** — xếp hạng sao + nhận xét (chỉ dành cho độc giả đã mượn sách)
- **Quản lý thể loại** — thêm/sửa/xóa inline không tải lại trang
- **Quản lý người dùng** — thay đổi vai trò, kích hoạt/vô hiệu hóa tài khoản
- **Tìm kiếm live** — cập nhật trang một phần bằng HTMX (không reload toàn trang)
- **Flash messages** — thông báo one-shot lưu cookie, tự ẩn
- **REST API** — JSON API đầy đủ tại `/api/v1/` kèm Swagger UI

---

## Tech Stack

| Tầng | Công nghệ |
|---|---|
| Ngôn ngữ | Python 3.12+ |
| Web framework | FastAPI ≥ 0.111 |
| ASGI server | Uvicorn ≥ 0.29 |
| ORM | SQLAlchemy 2.x (async) |
| Cơ sở dữ liệu | SQLite qua aiosqlite |
| Migration | Alembic ≥ 1.13 |
| Xác thực | PyJWT + bcrypt |
| Validation | Pydantic v2 + pydantic-settings |
| Templating | Jinja2 (SSR) |
| Tương tác frontend | HTMX 1.9 (CDN) |
| UI phía client | Alpine.js 3.x (CDN) |
| CSS | TailwindCSS CDN Play (JIT trên trình duyệt) |
| Biểu đồ | Chart.js 4 (CDN) |
| Testing | pytest + pytest-asyncio + httpx |
| Linting | Ruff |

---

## Cấu Trúc Dự Án

```
Python_LibraryManagement/
├── .env                        # Biến môi trường (git-ignored)
├── .env.example                # Template cấu hình
├── requirements.txt            # Danh sách dependencies Python
├── README.md
├── demo-flow.html              # Tài liệu demo luồng nghiệp vụ
├── docs/                       # Tài liệu phân tích & trình bày
└── backend/
    ├── alembic.ini             # Cấu hình Alembic
    ├── pytest.ini              # Cấu hình pytest
    ├── seed.py                 # Script tạo dữ liệu mẫu
    ├── library.db              # File SQLite (tự tạo khi chạy)
    ├── alembic/
    │   └── versions/
    │       └── 001_initial_schema.py
    ├── tests/
    │   ├── conftest.py
    │   ├── test_auth.py
    │   ├── test_books.py
    │   └── test_borrowings.py
    └── app/
        ├── main.py             # App factory, lifespan, middleware setup
        ├── core/
        │   ├── config.py       # Settings (pydantic-settings, đọc ../.env)
        │   └── security.py     # JWT helpers, bcrypt hash/verify
        ├── db/
        │   ├── base.py         # DeclarativeBase SQLAlchemy
        │   └── session.py      # Async engine + session factory + get_db()
        ├── models/             # SQLAlchemy ORM models (User, Book, Category, Borrowing, Review)
        ├── schemas/            # Pydantic v2 schemas (request/response)
        ├── repositories/       # Data access layer (async DB queries)
        ├── services/           # Business logic layer
        ├── dependencies/       # FastAPI DI — xác thực JWT (API) và RBAC
        ├── middleware/
        │   └── logging.py      # Access log middleware
        ├── api/v1/             # REST API routers (/api/v1/...)
        ├── web/                # Web UI routers (SSR Jinja2)
        │   ├── auth.py         # /login, /register, /logout
        │   ├── site.py         # /, /books, /books/{id}
        │   ├── dependencies.py # Cookie-based auth dependencies
        │   ├── templating.py   # render() helper + flash message
        │   ├── exceptions.py   # WebAuthRequired, WebForbidden
        │   ├── admin/          # /admin/* — quản trị
        │   └── reader/         # /reader/* — độc giả
        ├── templates/          # Jinja2 HTML templates
        │   ├── base.html       # Layout chính (sidebar + topbar)
        │   ├── auth/
        │   ├── site/
        │   ├── books/
        │   ├── admin/
        │   ├── reader/
        │   ├── partials/       # HTMX fragments (book_card, pagination, flash)
        │   └── errors/         # 403.html, 404.html
        ├── static/
        │   ├── css/app.css
        │   ├── js/app.js
        │   └── uploads/        # Ảnh bìa sách upload (đặt tên theo ISBN)
        └── utils/
            └── pagination.py   # Paginator helper
```

---

## Cài Đặt và Chạy Ứng Dụng

### Yêu Cầu

- Python 3.12 trở lên
- `pip` (đi kèm Python)

### 1. Tạo và kích hoạt virtual environment

```bash
# Từ thư mục Python_LibraryManagement/
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# Windows CMD
.venv\Scripts\activate.bat

# Linux / macOS
source .venv/bin/activate
```

### 2. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 3. Cấu hình môi trường

```bash
# Copy file mẫu vào Python_LibraryManagement/.env
cp .env.example .env        # Linux/macOS
copy .env.example .env      # Windows
```

Sau đó mở `.env` và thiết lập tối thiểu:

```env
SECRET_KEY=<chuỗi ngẫu nhiên ≥ 32 ký tự>
ENVIRONMENT=development
```

---

## Biến Môi Trường

File `.env` đặt tại thư mục gốc `Python_LibraryManagement/` (một cấp trên `backend/`).

| Biến | Mặc định | Mô tả |
|---|---|---|
| `SECRET_KEY` | _(bắt buộc)_ | Khóa ký JWT — dùng chuỗi ngẫu nhiên dài trong production |
| `ALGORITHM` | `HS256` | Thuật toán JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Thời hạn access token (phút) |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Thời hạn refresh token (ngày) |
| `DATABASE_URL` | `sqlite+aiosqlite:///./library.db` | SQLAlchemy async database URL |
| `ENVIRONMENT` | `production` | `development` tự động tạo bảng khi khởi động |
| `DEBUG` | `false` | Bật log SQL query của SQLAlchemy |
| `BORROWING_PERIOD_DAYS` | `14` | Thời hạn mượn mặc định (ngày) |
| `MAX_RENEWALS` | `2` | Số lần gia hạn tối đa mỗi phiếu mượn |
| `FINE_PER_DAY` | `5000.0` | Phí phạt quá hạn (VND/ngày) |
| `MAX_ACTIVE_BORROWINGS` | `5` | Số phiếu mượn đang active tối đa mỗi độc giả |
| `ADMIN_USERNAME` | `admin` | Tên đăng nhập tài khoản admin được seed |
| `ADMIN_EMAIL` | `admin@library.local` | Email tài khoản admin được seed |
| `ADMIN_PASSWORD` | `Admin@123456` | Mật khẩu tài khoản admin được seed |
| `ALLOWED_ORIGINS` | `["http://localhost:3000"]` | CORS allowed origins (JSON array) |

---

## Cơ Sở Dữ Liệu & Migration

### Tự động tạo bảng (development)

Khi `ENVIRONMENT=development`, bảng được tạo tự động lúc khởi động. Không cần chạy migration thủ công khi setup lần đầu.

### Chạy migration (production / tuỳ chọn)

```bash
cd backend
alembic upgrade head
```

---

## Seed Dữ Liệu Mẫu

Tạo dữ liệu mẫu gồm tài khoản, thể loại, sách, phiếu mượn và đánh giá:

```bash
cd backend
python seed.py
```

**Tài khoản mặc định sau khi seed:**

| Vai trò | Username | Mật khẩu |
|---|---|---|
| Admin | `admin` | `Admin@123456` |
| Thủ thư | `librarian1` | `Lib@123456` |
| Thủ thư | `librarian2` | `Lib@123456` |
| Độc giả | `tranvandoc` | `Reader@123` |
| Độc giả | `lethimuon` | `Reader@123` |
| _(và 27 độc giả khác)_ | — | `Reader@123` |

---

## Chạy Ứng Dụng

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Ứng dụng khởi động tại **`http://localhost:8000`**.

---

## Danh Sách URL

### Web UI

| URL | Mô tả | Quyền truy cập |
|---|---|---|
| `GET /` | Trang chủ — thống kê + sách nổi bật | Công khai |
| `GET /books` | Duyệt & tìm kiếm sách | Công khai |
| `GET /books/{id}` | Chi tiết sách + đánh giá | Công khai |
| `GET /login` | Form đăng nhập | Công khai |
| `GET /register` | Form đăng ký | Công khai |
| `POST /logout` | Xóa session cookie | Đã đăng nhập |
| `GET /reader/my-books` | Sách đang mượn | Reader+ |
| `GET /reader/history` | Lịch sử mượn đầy đủ | Reader+ |
| `GET /reader/profile` | Xem & cập nhật hồ sơ | Reader+ |
| `GET /reader/change-password` | Đổi mật khẩu | Reader+ |
| `GET /admin/dashboard` | Dashboard KPI + biểu đồ | Admin |
| `GET /admin/books` | Quản lý sách | Librarian+ |
| `GET /admin/books/new` | Thêm sách mới | Admin |
| `GET /admin/books/{id}/edit` | Sửa thông tin sách | Admin |
| `GET /admin/borrowings` | Xem tất cả phiếu mượn | Librarian+ |
| `GET /admin/borrowings/issue` | Cấp phát sách cho độc giả | Librarian+ |
| `GET /admin/borrowings/{id}/return` | Xử lý trả sách | Librarian+ |
| `GET /admin/categories` | Quản lý thể loại | Admin |
| `GET /admin/users` | Quản lý người dùng | Admin |

### Developer

| URL | Mô tả |
|---|---|
| `http://localhost:8000/api/docs` | Swagger UI |
| `http://localhost:8000/api/redoc` | ReDoc |
| `http://localhost:8000/health` | Health check |

---

## API Reference

Tất cả REST endpoints có prefix `/api/v1/`. Xác thực dùng `Authorization: Bearer <token>`.

Lấy token qua `POST /api/v1/auth/login` với form fields `username` và `password` (OAuth2 password flow).

| Resource | Endpoints |
|---|---|
| Auth | `POST /auth/login`, `/auth/register`, `/auth/refresh`, `/auth/change-password`, `GET /auth/me` |
| Books | `GET/POST /books`, `GET/PATCH /books/{id}`, `DELETE /books/{id}` |
| Categories | `GET/POST /categories`, `GET/PATCH /categories/{id}`, `DELETE /categories/{id}` |
| Borrowings | `GET/POST /borrowings`, `GET /borrowings/{id}`, `POST /borrowings/{id}/return`, `/renew`, `/mark-fine-paid` |
| Reviews | `GET/POST /reviews`, `PATCH /reviews/{id}`, `PATCH /reviews/{id}/status`, `DELETE /reviews/{id}` |
| Users | `GET/POST /users`, `GET/PATCH /users/me`, `GET/PATCH/DELETE /users/{id}` |
| Dashboard | `GET /dashboard/stats`, `/popular-books`, `/active-readers`, `/monthly-stats` |

---

## Chạy Tests

```bash
cd backend
pytest -v
```

Phạm vi test: xác thực (đăng ký/đăng nhập/JWT), sách (CRUD, phân quyền, validation), phiếu mượn (cấp phát/trả, giới hạn gia hạn, kiểm tra tồn kho).

---

## Phân Quyền

| Chức năng | Reader | Librarian | Admin |
|---|---|---|---|
| Duyệt sách / xem chi tiết | ✓ | ✓ | ✓ |
| Xem phiếu mượn của bản thân | ✓ | ✓ | ✓ |
| Gia hạn phiếu mượn của bản thân | ✓ | ✓ | ✓ |
| Viết đánh giá sách | ✓ | ✓ | ✓ |
| Cấp phát / xử lý trả sách | — | ✓ | ✓ |
| Xem tất cả phiếu mượn | — | ✓ | ✓ |
| Thêm / sửa sách | — | — | ✓ |
| Xóa sách | — | — | ✓ |
| Quản lý thể loại | — | — | ✓ |
| Quản lý người dùng | — | — | ✓ |
| Xem dashboard thống kê | — | — | ✓ |

---

## Quy Tắc Nghiệp Vụ

- **Thời hạn mượn:** 14 ngày (cấu hình qua `BORROWING_PERIOD_DAYS`)
- **Số lần gia hạn tối đa:** 2 lần mỗi phiếu mượn (cấu hình qua `MAX_RENEWALS`)
- **Số phiếu mượn active tối đa:** 5 phiếu/độc giả (cấu hình qua `MAX_ACTIVE_BORROWINGS`)
- **Phí phạt quá hạn:** 5.000 VND/ngày (cấu hình qua `FINE_PER_DAY`)
- **Đánh giá sách:** Độc giả phải đã mượn sách ít nhất 1 lần mới được đánh giá; mỗi độc giả chỉ được 1 đánh giá/sách
- **Xóa sách:** Bị chặn nếu sách đang có phiếu mượn active (chưa trả)
- **Xóa người dùng:** Bị chặn ở DB level nếu người dùng còn phiếu mượn (RESTRICT constraint)
