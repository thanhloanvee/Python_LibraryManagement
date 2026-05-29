# DESIGN_DOC.md — Library Management System
## Presentation Design Context

> Tài liệu này được tạo cho mục đích trình bày (PowerPoint / Gamma / Canva AI).
> Tập trung vào hiểu biết nghiệp vụ, giới thiệu công nghệ và tổng quan hệ thống.

---

## 1. Project Introduction

**Tên dự án:** Library Management System (LMS)

**Một câu mô tả:**
> Hệ thống quản lý thư viện trực tuyến, số hoá toàn bộ quy trình từ tra cứu sách, mượn/trả, đến theo dõi tồn kho và thống kê hoạt động.

**Bối cảnh ra đời:**
Hệ thống được xây dựng lại từ nền tảng PHP/Yii2 cũ sang Python/FastAPI hiện đại — một dự án tái cấu trúc (rewrite) hoàn toàn, giữ nguyên nghiệp vụ nhưng nâng cấp toàn bộ công nghệ.

**Điểm nổi bật:**
- Vừa là ứng dụng Web hoàn chỉnh (giao diện HTML đầy đủ)
- Vừa là REST API có thể tích hợp với bất kỳ frontend nào
- Giao diện phản hồi nhanh nhờ HTMX — không cần reload trang khi tìm kiếm
- Tự động hóa tính phí phạt, theo dõi tồn kho theo thời gian thực

---

## 2. System Objectives

### Mục tiêu chính

| # | Mục tiêu | Giải pháp trong hệ thống |
|---|---|---|
| 1 | Số hoá phiếu mượn/trả | Module Borrowing với đầy đủ trạng thái: borrowed → returned / overdue |
| 2 | Kiểm soát tồn kho real-time | Trường `available_quantity` cập nhật ngay khi mượn/trả |
| 3 | Tự động tính phí phạt | `fine_amount = days_overdue × 5,000 VND` — tính tại thời điểm trả |
| 4 | Phân quyền rõ ràng | RBAC 3 cấp: Reader / Librarian / Admin |
| 5 | Thống kê quản lý | Admin Dashboard: KPI, biểu đồ tháng, top sách/độc giả |
| 6 | Trải nghiệm tra cứu | Tìm kiếm full-text, lọc đa tiêu chí, không cần đăng nhập |

### Phạm vi hệ thống

**Trong phạm vi:**
- Quản lý kho sách (CRUD, ảnh bìa, thể loại)
- Luồng lưu thông sách (mượn, trả, gia hạn, phạt)
- Quản lý tài khoản người dùng và phân quyền
- Báo cáo thống kê và dashboard
- Đánh giá sách bởi độc giả

**Ngoài phạm vi:**
- Thanh toán trực tuyến (tiền phạt ghi nhận thủ công)
- Đặt trước / đặt giữ sách (reservation)
- Gửi email/SMS nhắc nhở
- Ứng dụng di động

---

## 3. Target Users

### 3 nhóm người dùng chính

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   👤 READER (Độc giả)          Người dùng cuối          │
│   • Duyệt và tìm kiếm sách     • Tự đăng ký tài khoản  │
│   • Xem sách đang mượn          • Gia hạn tự phục vụ   │
│   • Viết đánh giá sách                                  │
│                                                         │
│   📚 LIBRARIAN (Thủ thư)       Nhân viên thư viện       │
│   • Cấp phát sách cho reader    • Xử lý trả sách        │
│   • Quản lý tất cả phiếu mượn  • Theo dõi sách quá hạn │
│                                                         │
│   ⚙️  ADMIN (Quản trị viên)    Ban quản lý              │
│   • Toàn quyền hệ thống         • Xem dashboard & báo cáo│
│   • Quản lý sách, thể loại     • Quản lý tài khoản      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Nhu cầu từng nhóm

| Nhóm | Nhu cầu cốt lõi | Tính năng chính |
|---|---|---|
| Độc giả | Tìm sách nhanh, biết sách có sẵn không | Search, filter, book detail, my-books |
| Thủ thư | Xử lý mượn/trả nhanh, không nhầm lẫn | Live search issue form, return form, fine calc |
| Admin | Nắm bắt tình hình thư viện tổng thể | Dashboard, charts, reports, user management |

---

## 4. Technology Stack

### Tổng quan công nghệ

```
┌──────────────────────────────────────────────────────────┐
│  FRONTEND (Browser)                                      │
│  TailwindCSS · Alpine.js · HTMX · Chart.js               │
├──────────────────────────────────────────────────────────┤
│  WEB SERVER (FastAPI + Uvicorn)                          │
│  ┌─────────────────┐    ┌──────────────────────────┐    │
│  │  Web UI (Jinja2) │    │  REST API (/api/v1/)      │    │
│  │  Server-Side     │    │  JSON responses           │    │
│  │  Rendering       │    │  Swagger UI               │    │
│  └─────────────────┘    └──────────────────────────┘    │
├──────────────────────────────────────────────────────────┤
│  BUSINESS LAYER                                          │
│  Services (Python) · Pydantic v2 · PyJWT · bcrypt        │
├──────────────────────────────────────────────────────────┤
│  DATA LAYER                                              │
│  SQLAlchemy (async ORM) · Alembic (migrations)           │
├──────────────────────────────────────────────────────────┤
│  DATABASE                                                │
│  SQLite (aiosqlite driver)                               │
└──────────────────────────────────────────────────────────┘
```

### Giải thích vai trò từng công nghệ

**Python 3.12+ — Ngôn ngữ lập trình**
- Lý do chọn: Cú pháp rõ ràng, hệ sinh thái phong phú, typing mạnh với Pydantic
- Vai trò: Nền tảng toàn bộ backend

**FastAPI — Web Framework**
- Lý do chọn: Async-native, tự động sinh OpenAPI docs, validation tích hợp qua Pydantic
- Vai trò: Xử lý HTTP requests, routing, dependency injection, phục vụ cả Web UI và REST API

**Uvicorn — ASGI Server**
- Lý do chọn: Server async hiệu suất cao, chuẩn cho FastAPI
- Vai trò: Khởi chạy ứng dụng, xử lý kết nối đến

**SQLite + aiosqlite — Database**
- Lý do chọn: Zero-config, phù hợp cho dự án học thuật/nhỏ vừa, không cần cài thêm server DB
- Vai trò: Lưu trữ toàn bộ dữ liệu trong file `library.db`

**SQLAlchemy 2.x (async) — ORM**
- Lý do chọn: ORM chuẩn Python, hỗ trợ async, declarative models rõ ràng
- Vai trò: Ánh xạ Python class ↔ bảng database, quản lý session, truy vấn async

**Alembic — Database Migrations**
- Lý do chọn: Tool migration chính thống của SQLAlchemy
- Vai trò: Quản lý lịch sử thay đổi schema database, có thể rollback

**PyJWT + bcrypt — Authentication & Security**
- Lý do chọn: Chuẩn công nghiệp, thay thế các thư viện cũ đã ngừng bảo trì
- Vai trò: PyJWT tạo/xác thực access token & refresh token; bcrypt hash/verify mật khẩu

**Pydantic v2 — Validation**
- Lý do chọn: Validation cực nhanh (Rust core), tích hợp tự nhiên với FastAPI
- Vai trò: Xác thực dữ liệu đầu vào, serialize/deserialize request-response

**Jinja2 — Templating**
- Lý do chọn: Template engine chuẩn Python, linh hoạt, hỗ trợ kế thừa template
- Vai trò: Render HTML phía server, dùng cho toàn bộ giao diện web

**HTMX — Partial Page Updates**
- Lý do chọn: Tăng tính phản hồi UI mà không cần viết JavaScript; server vẫn render HTML
- Vai trò: Live search (tìm user/sách khi cấp phát), inline CRUD thể loại, dynamic table rows

**Alpine.js — Client-side Reactivity**
- Lý do chọn: Nhẹ (~15KB), declarative trong HTML, không cần build step
- Vai trò: Dropdown menu, sidebar toggle, modal, các tương tác UI nhỏ

**TailwindCSS — CSS Framework**
- Lý do chọn: Utility-first, không cần viết CSS tùy chỉnh nhiều, dùng CDN không cần build
- Vai trò: Styling toàn bộ giao diện, responsive design

**Chart.js — Data Visualization**
- Lý do chọn: Thư viện biểu đồ phổ biến, dễ tích hợp, đẹp mắt
- Vai trò: Vẽ biểu đồ cột mượn/trả theo tháng trên admin dashboard

---

## 5. System Architecture Overview

### Kiến trúc tổng quan

**Loại kiến trúc:** Monolithic Full-Stack Web Application

```
                    ┌─────────────────────────────┐
                    │         BROWSER              │
                    │  HTML + CSS + JS (HTMX/Alpine)│
                    └────────────┬────────────────┘
                                 │ HTTP
                    ┌────────────▼────────────────┐
                    │       FastAPI App            │
                    │    (Uvicorn ASGI Server)     │
                    │                             │
                    │  ┌──────────┐ ┌──────────┐  │
                    │  │ Web UI   │ │REST API  │  │
                    │  │/…        │ │/api/v1/… │  │
                    │  └────┬─────┘ └────┬─────┘  │
                    │       └─────┬──────┘         │
                    │      ┌──────▼──────┐          │
                    │      │  Services  │          │
                    │      │(Biz Logic) │          │
                    │      └──────┬──────┘          │
                    │      ┌──────▼──────┐          │
                    │      │Repositories│          │
                    │      │(DB Queries)│          │
                    │      └──────┬──────┘          │
                    └─────────────┼────────────────┘
                                 │ SQLAlchemy async
                    ┌────────────▼────────────────┐
                    │    SQLite (library.db)       │
                    └─────────────────────────────┘
```

### Hai giao diện trên cùng một server

| Giao diện | URL prefix | Phục vụ | Auth |
|---|---|---|---|
| Web UI | `/`, `/books`, `/admin/*`, `/reader/*` | Trình duyệt (HTML) | httponly cookie |
| REST API | `/api/v1/*` | Mobile / 3rd party / Swagger UI | Bearer JWT token |

### Pattern phân tầng (Layered Architecture)

```
Request → [Router] → [Service] → [Repository] → [Database]
                         ↓
                  [Business Rules]
                  (validation, fine calc, stock check)
```

- **Router:** Nhận request, parse params, gọi service, trả response
- **Service:** Toàn bộ logic nghiệp vụ, kiểm tra điều kiện, phối hợp repositories
- **Repository:** Truy vấn database thuần túy, không có business logic
- **Model:** SQLAlchemy ORM — định nghĩa cấu trúc bảng, quan hệ

---

## 6. Database Design Summary

### 5 bảng chính

| Bảng | Số cột | Mục đích |
|---|---|---|
| `users` | 11 | Tài khoản người dùng (reader / librarian / admin) |
| `categories` | 4 | Phân loại sách |
| `books` | 15 | Kho sách với tồn kho động |
| `borrowings` | 14 | Phiếu mượn — trung tâm của hệ thống |
| `reviews` | 8 | Đánh giá sách (1 user / 1 sách) |

### Các trường đặc biệt đáng chú ý

**Bảng `books`:**
- `quantity` — tổng số bản sách nhập về
- `available_quantity` — số bản hiện đang có sẵn để mượn (tự động +/- khi mượn/trả)
- `status` — Có sẵn / Hư hỏng / Mất

**Bảng `borrowings`:**
- `fine_amount` — tiền phạt (VND), tính tự động khi trả trễ
- `fine_paid` — boolean xác nhận đã thu phạt
- `renewed_count` — số lần đã gia hạn (giới hạn 2 lần)
- `book_condition` — tình trạng sách khi trả (good / fair / poor / damaged)

### Ràng buộc toàn vẹn dữ liệu

| Quan hệ | Chiến lược xóa | Lý do |
|---|---|---|
| Category → Books | SET NULL | Sách không bị mất khi xóa thể loại |
| User → Borrowings | RESTRICT | Bảo vệ lịch sử mượn sách |
| Book → Borrowings | RESTRICT | Bảo vệ lịch sử mượn sách |
| User → Reviews | CASCADE | Xóa user thì xóa cả reviews |
| Book → Reviews | CASCADE | Xóa sách thì xóa cả reviews |

---

## 7. ERD Description

### Sơ đồ quan hệ thực thể

```
┌──────────────┐           ┌──────────────────────┐
│  categories  │ 1       N │        books          │
│──────────────│───────────│──────────────────────│
│ id (PK)      │           │ id (PK)              │
│ name         │           │ title                │
│ description  │           │ author               │
└──────────────┘           │ isbn (UNIQUE)        │
                           │ publisher            │
                           │ publication_year     │
                           │ language             │
                           │ quantity             │
                           │ available_quantity   │
                           │ status               │
                           │ cover_image          │
                           │ category_id (FK) ────┘
                           └──────────┬───────────┘
                                      │ 1            1
                           ┌──────────┼──────────────┐
                           │ N        │              │ N
              ┌────────────▼──┐   ┌───▼──────────────▼──┐
              │  borrowings   │   │       reviews        │
              │───────────────│   │──────────────────────│
              │ id (PK)       │   │ id (PK)              │
              │ user_id (FK)──┼─┐ │ book_id (FK)         │
              │ book_id (FK)  │ │ │ user_id (FK) ────────┼─┐
              │ borrow_date   │ │ │ rating (1–5)         │ │
              │ due_date      │ │ │ comment              │ │
              │ return_date   │ │ │ status               │ │
              │ status        │ │ └──────────────────────┘ │
              │ fine_amount   │ │                          │
              │ fine_paid     │ │  ┌───────────────────┐   │
              │ renewed_count │ └──┤      users        ├───┘
              │ book_condition│    │───────────────────│
              └───────────────┘    │ id (PK)           │
                                   │ username (UNIQUE) │
                                   │ email (UNIQUE)    │
                                   │ password_hash     │
                                   │ full_name         │
                                   │ phone             │
                                   │ address           │
                                   │ role              │
                                   │ status            │
                                   └───────────────────┘
```

### Quan hệ tóm tắt

| Quan hệ | Loại | Ghi chú |
|---|---|---|
| Category → Books | 1 – N | Một thể loại có nhiều sách |
| User → Borrowings | 1 – N | Một reader có nhiều phiếu mượn |
| Book → Borrowings | 1 – N | Một sách có nhiều lượt mượn |
| User → Reviews | 1 – N | Một user có thể viết nhiều review (mỗi sách 1 lần) |
| Book → Reviews | 1 – N | Một sách có thể có nhiều review |
| User + Book → Review | UNIQUE | Ràng buộc unique `(user_id, book_id)` |

---

## 8. Business Logic Flow

### Luồng 1 — Mượn sách (Issue Book)

```
[Thủ thư]
    │
    ▼
Tìm kiếm Reader          ← HTMX live search (gõ tên/username)
    │
    ▼
Tìm kiếm Sách            ← HTMX live search (gõ tên/ISBN)
    │
    ▼
Chọn ngày trả            ← Mặc định: hôm nay + 14 ngày
    │
    ▼
Hệ thống kiểm tra:
  ✓ Reader tồn tại & active?
  ✓ Sách available_quantity > 0?
  ✓ Reader < 5 phiếu đang mượn?
  ✓ Reader chưa mượn sách này?
    │
    ├── ✗ → Thông báo lỗi cụ thể
    │
    └── ✓ → Tạo phiếu mượn
              Giảm available_quantity -= 1
              Redirect về danh sách phiếu mượn
```

### Luồng 2 — Trả sách (Return Book)

```
[Thủ thư]
    │
    ▼
Tìm phiếu mượn đang active
    │
    ▼
Ghi nhận tình trạng sách    ← good / fair / poor / damaged
    │
    ▼
Hệ thống tính phạt:
  • Nếu return_date > due_date:
    fine_amount = (return_date − due_date) × 5,000 VND
  • Ngược lại: fine_amount = 0
    │
    ▼
Cập nhật phiếu mượn:
  status = RETURNED
  return_date = hôm nay
    │
    ▼
Tăng available_quantity += 1
    │
    ▼
Thủ thư thu tiền phạt (nếu có)
    │
    ▼
Click "Đánh dấu đã thanh toán" → fine_paid = true
```

### Luồng 3 — Gia hạn (Renew)

```
[Reader / Thủ thư]
    │
    ▼
Chọn phiếu mượn muốn gia hạn
    │
    ▼
Kiểm tra:
  ✓ Phiếu đang BORROWED (chưa trả, chưa bị block)?
  ✓ renewed_count < 2?
    │
    ├── ✗ → Thông báo không thể gia hạn
    │
    └── ✓ → due_date += 14 ngày
              renewed_count += 1
```

### Luồng 4 — Độc giả tự phục vụ

```
[Reader] (không cần đăng nhập)
    │
    ▼
Duyệt sách / Tìm kiếm
    │
    ▼
Xem chi tiết sách + reviews + điểm trung bình
    │
    ▼ (cần đăng nhập để tiếp tục)
Đăng nhập / Đăng ký
    │
    ▼
Xem danh sách sách đang mượn
    │
    ▼
Gia hạn (nếu chưa đủ 2 lần)
    │
    ▼
Sau khi trả sách → Viết đánh giá (1–5 sao + nhận xét)
```

---

## 9. Roles & Permissions Summary

### Phân cấp quyền hạn

```
ADMIN
  └── Toàn quyền: sách, thể loại, users, dashboard, mượn/trả
  
LIBRARIAN
  └── Mượn/trả sách, xem tất cả phiếu mượn, tìm kiếm
  
READER
  └── Duyệt sách, xem phiếu mượn của mình, gia hạn, đánh giá
  
PUBLIC (chưa đăng nhập)
  └── Xem danh sách sách, xem chi tiết sách
```

### Ma trận quyền chính

| Chức năng | Public | Reader | Librarian | Admin |
|---|---|---|---|---|
| Duyệt & tìm kiếm sách | ✓ | ✓ | ✓ | ✓ |
| Xem chi tiết + reviews | ✓ | ✓ | ✓ | ✓ |
| Xem phiếu mượn của mình | — | ✓ | ✓ | ✓ |
| Gia hạn phiếu của mình | — | ✓ | ✓ | ✓ |
| Viết đánh giá sách | — | ✓ | ✓ | ✓ |
| Cấp phát / trả sách | — | — | ✓ | ✓ |
| Xem tất cả phiếu mượn | — | — | ✓ | ✓ |
| Thêm / sửa / xóa sách | — | — | — | ✓ |
| Quản lý thể loại | — | — | — | ✓ |
| Quản lý người dùng | — | — | — | ✓ |
| Xem dashboard & thống kê | — | — | — | ✓ |

### Quy tắc đặc biệt

- **Đọc giả tự đăng ký:** Chỉ tạo được tài khoản `reader`, không tự lên `librarian`/`admin`
- **Giới hạn mượn:** Tối đa 5 phiếu mượn đang active cùng lúc / reader
- **Giới hạn gia hạn:** Tối đa 2 lần / phiếu mượn
- **Điều kiện review:** Phải đã mượn sách ít nhất 1 lần
- **Xóa an toàn:** Không xóa được sách/user khi còn phiếu mượn active

---

## 10. Functional Overview

### Module 1 — Catalogue (Tra cứu sách)

| Tính năng | Mô tả | Người dùng |
|---|---|---|
| Duyệt sách | Danh sách với phân trang, lọc theo thể loại / ngôn ngữ / trạng thái | Tất cả |
| Tìm kiếm | Full-text search (tiêu đề, tác giả, ISBN) | Tất cả |
| Chi tiết sách | Thông tin đầy đủ, ảnh bìa, tồn kho, đánh giá | Tất cả |
| Trang chủ | Thống kê nhanh + sách nổi bật | Tất cả |

### Module 2 — Authentication (Xác thực)

| Tính năng | Mô tả | Người dùng |
|---|---|---|
| Đăng ký | Tạo tài khoản reader mới | Public |
| Đăng nhập | JWT httponly cookie (Web) / Bearer token (API) | Tất cả |
| Đổi mật khẩu | Xác thực mật khẩu cũ trước khi đổi | Reader+ |
| Cập nhật hồ sơ | Sửa tên, phone, địa chỉ | Reader+ |

### Module 3 — Circulation (Lưu thông sách)

| Tính năng | Mô tả | Người dùng |
|---|---|---|
| Cấp phát sách | Live search reader + sách, thiết lập hạn trả | Librarian+ |
| Xử lý trả sách | Ghi tình trạng, tính phạt tự động | Librarian+ |
| Gia hạn | Tự phục vụ hoặc qua thủ thư, max 2 lần | Reader+ |
| Theo dõi phiếu | Xem tất cả phiếu, lọc quá hạn / theo trạng thái | Librarian+ |
| Thu phạt | Đánh dấu tiền phạt đã thanh toán | Librarian+ |

### Module 4 — Catalogue Management (Quản lý kho)

| Tính năng | Mô tả | Người dùng |
|---|---|---|
| Thêm sách | Form đầy đủ, upload ảnh bìa | Admin |
| Sửa sách | Cập nhật thông tin, thay ảnh bìa | Admin |
| Xóa sách | Chặn nếu còn phiếu active | Admin |
| Quản lý thể loại | CRUD inline không reload trang (HTMX) | Admin |

### Module 5 — User Management (Quản lý người dùng)

| Tính năng | Mô tả | Người dùng |
|---|---|---|
| Danh sách users | Tìm kiếm, lọc theo role / status | Admin |
| Thay đổi role | Reader → Librarian / Admin | Admin |
| Khoá tài khoản | Activate / deactivate | Admin |
| Xóa tài khoản | Chặn nếu còn phiếu mượn | Admin |

### Module 6 — Dashboard & Analytics (Thống kê)

| Tính năng | Mô tả | Người dùng |
|---|---|---|
| KPI Cards | Tổng sách, readers, phiếu active, quá hạn, tiền phạt | Admin |
| Biểu đồ tháng | Chart.js — số lượng mượn/trả mỗi tháng trong năm | Admin |
| Top sách | 5 sách được mượn nhiều nhất | Admin |
| Top độc giả | 5 reader mượn sách nhiều nhất | Admin |
| Tồn kho | Danh sách sách với số bản hiện có, sắp xếp theo mức thấp nhất | Admin |

### Module 7 — Reviews (Đánh giá)

| Tính năng | Mô tả | Người dùng |
|---|---|---|
| Viết review | Rating 1–5 sao + nhận xét (cần đã mượn) | Reader+ |
| Xem reviews | Hiển thị trên trang chi tiết sách | Tất cả |
| Ẩn/hiện review | Kiểm duyệt review không phù hợp | Admin |

---

## 11. User Journey

### Journey 1 — Độc giả mới

```
1. Truy cập trang chủ (/)
   → Thấy thống kê thư viện + sách nổi bật

2. Duyệt sách (/books)
   → Tìm kiếm theo tên/tác giả
   → Lọc theo thể loại
   → Xem chi tiết sách (ảnh bìa, mô tả, tồn kho)

3. Đăng ký tài khoản (/register)
   → Nhập username, email, mật khẩu, họ tên

4. Đăng nhập (/login)
   → Được redirect về trang trước đó

5. Liên hệ thủ thư để mượn sách
   (Reader không tự mượn được qua web, phải qua thủ thư)

6. Xem sách đang mượn (/reader/my-books)
   → Biết hạn trả, trạng thái
   → Gia hạn nếu cần

7. Trả sách tại quầy
   → Thủ thư xử lý return trên hệ thống

8. Viết đánh giá (/books/{id})
   → Rating + nhận xét sau khi trả sách
```

### Journey 2 — Thủ thư xử lý một ca mượn

```
1. Đăng nhập với tài khoản librarian

2. Reader đến quầy muốn mượn sách
   → Vào /admin/borrowings/issue

3. Gõ tên reader → live search hiện danh sách → chọn reader

4. Gõ tên sách → live search hiện sách có sẵn → chọn sách

5. Xác nhận ngày trả (mặc định +14 ngày)
   → Submit → Phiếu mượn #XYZ được tạo

6. Reader trả sách sau đó
   → Vào /admin/borrowings → Tìm phiếu → Click "Trả sách"
   → Ghi nhận tình trạng sách
   → Hệ thống tự tính phạt (nếu trễ)
   → Thu phạt → Click "Đánh dấu đã thanh toán"
```

### Journey 3 — Admin xem báo cáo cuối tháng

```
1. Đăng nhập với tài khoản admin

2. Vào /admin/dashboard

3. Xem KPI:
   • Tổng số phiếu đang mượn
   • Số phiếu quá hạn
   • Tiền phạt chưa thu

4. Xem biểu đồ → chọn năm → so sánh mượn/trả từng tháng

5. Xem top 5 sách được mượn nhiều nhất

6. Xem danh sách tồn kho → phát hiện sách sắp hết bản

7. Vào /admin/books → Thêm sách mới nếu cần
```

---

## 12. System Limitations

Những hạn chế có thể thấy rõ từ cài đặt hiện tại:

### Hạn chế kỹ thuật

| Hạn chế | Giải thích |
|---|---|
| **SQLite single-file** | Không phù hợp cho môi trường production nhiều user đồng thời; phù hợp cho project học thuật / thư viện nhỏ |
| **No reservation system** | Độc giả không thể đặt giữ sách khi sách đang hết; phải hỏi trực tiếp thủ thư |
| **Sync overdue thủ công** | Trạng thái OVERDUE chỉ cập nhật khi Admin kích hoạt; không có background job tự động |
| **TailwindCSS qua CDN** | Không nén/tối ưu CSS; phù hợp dev nhưng chậm hơn cho production |
| **No email notifications** | Không có thông báo email nhắc hạn trả, thông báo sách quá hạn |
| **File upload local** | Ảnh bìa lưu trực tiếp trên server, không dùng cloud storage |

### Hạn chế nghiệp vụ

| Hạn chế | Giải thích |
|---|---|
| **Reader không tự mượn** | Phải qua thủ thư, không có flow self-service hoàn toàn |
| **Thanh toán tiền phạt offline** | Hệ thống chỉ ghi nhận, không xử lý thanh toán thật |
| **Không có lịch sử audit** | Không theo dõi ai đã thay đổi gì (audit trail) |
| **Không hỗ trợ multi-language** | Giao diện hỗ trợ sách Tiếng Việt + Tiếng Anh nhưng UI hoàn toàn là tiếng Anh/Việt pha |

---

## 13. Recommended Presentation Story Flow

### Gợi ý trình tự slide tối ưu cho buổi bảo vệ

```
Slide 1 — Giới thiệu đề tài
  "Bài toán thư viện truyền thống và giải pháp số hoá"

  ↓

Slide 2 — Mục tiêu hệ thống
  "5 mục tiêu cốt lõi, business rules đã được mã hoá"

  ↓

Slide 3 — Công nghệ sử dụng
  "Stack Python hiện đại — tại sao chọn FastAPI, SQLite, HTMX?"

  ↓

Slide 4 — Kiến trúc hệ thống
  "Monolith Full-stack: Web UI + REST API trên 1 server"
  "Layered architecture: Router → Service → Repository → DB"

  ↓

Slide 5 — Cấu trúc dự án
  "Tổ chức thư mục rõ ràng, phân tách trách nhiệm"

  ↓

Slide 6 — ERD & Thiết kế database
  "5 bảng, quan hệ, ràng buộc toàn vẹn dữ liệu"

  ↓

Slide 7 — Business Logic Flow
  "Demo luồng mượn sách: 5 bước kiểm tra, auto fine calc"

  ↓

Slide 8 — Roles & Phân quyền
  "RBAC 3 cấp — Reader / Librarian / Admin"

  ↓

Slide 9 — Chức năng hệ thống & Giao diện
  "Demo / Screenshot: Dashboard, Issue form, Book list"

  ↓

Slide 10 — Kết luận, Hạn chế & Hướng phát triển
  "Những gì đã làm được — những gì còn thiếu — bước tiếp theo"
```

### Điểm nhấn nên đề cập khi trình bày

1. **Async architecture** — FastAPI + SQLAlchemy async → xử lý đồng thời tốt
2. **Dual interface** — Cùng 1 server phục vụ cả Web UI và REST API
3. **HTMX live search** — Demo trực tiếp tính năng này ấn tượng
4. **Auto fine calculation** — Logic tính phạt tự động, không cần nhập tay
5. **RBAC enforcement** — Phân quyền enforce ở cả Web và API layer
6. **Swagger UI** — REST API tự document, professional

### Thứ tự ưu tiên demo (nếu có thời gian)

1. Trang chủ + duyệt sách (public, ấn tượng ngay)
2. Issue form với live search (HTMX)
3. Admin dashboard với biểu đồ Chart.js
4. Swagger UI tại `/api/docs`
