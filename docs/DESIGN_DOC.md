# DESIGN_DOC.md — Presentation Design Context
## Hệ Thống Quản Lý Thư Viện (Library Management System)

> Tài liệu này được thiết kế để làm nguồn ngữ cảnh chính cho các công cụ tạo slide AI (Gamma, Canva AI, Beautiful.ai, PowerPoint Copilot).
> Tập trung vào: hiểu nghiệp vụ · giới thiệu công nghệ · tổng quan hệ thống.

---

## 1. Project Introduction

**Tên đề tài:** Hệ Thống Quản Lý Thư Viện Trực Tuyến

**Một câu mô tả:**
Ứng dụng web full-stack bằng Python giúp thư viện số hoá toàn bộ quy trình mượn/trả sách, quản lý kho sách theo thời gian thực và cung cấp thống kê hoạt động cho ban quản lý.

**Bối cảnh:**
Thư viện truyền thống vận hành bằng sổ sách giấy — gây khó khăn trong kiểm soát tồn kho, theo dõi sách quá hạn và tổng hợp báo cáo. Hệ thống này thay thế hoàn toàn quy trình thủ công đó bằng một nền tảng web hiện đại, bất đồng bộ, có REST API và giao diện thân thiện.

**Phạm vi:**
- Quản lý kho sách (thêm, sửa, xóa, upload ảnh bìa, phân loại)
- Lưu thông sách (mượn, trả, gia hạn, phí phạt tự động)
- Phân quyền 3 vai trò (Reader · Librarian · Admin)
- Dashboard thống kê trực quan (biểu đồ, KPI, top sách/người dùng)
- REST API đầy đủ với tài liệu tự động (Swagger UI)

---

## 2. System Objectives

### Mục tiêu chức năng

| # | Mục tiêu | Kết quả cụ thể |
|---|---|---|
| 1 | Số hoá lưu thông sách | Tạo/theo dõi phiếu mượn, cập nhật tồn kho tức thời |
| 2 | Tự động hoá phí phạt | Tính phạt = số ngày quá hạn × 5.000 VND, không cần tính tay |
| 3 | Kiểm soát tồn kho real-time | `available_quantity` cập nhật ngay khi cấp phát / trả sách |
| 4 | Thống kê hoạt động | Dashboard KPI + biểu đồ mượn/trả theo tháng + top sách/reader |
| 5 | Tìm kiếm & duyệt sách | Full-text search, lọc thể loại/ngôn ngữ/trạng thái, phân trang |
| 6 | Đánh giá sách cộng đồng | Reader đã mượn sách được đánh giá 1–5 sao + nhận xét |

### Mục tiêu kỹ thuật

- Áp dụng kiến trúc phân tầng rõ ràng (Layered Architecture) với Python
- Xây dựng đồng thời REST API và Web UI trong một ứng dụng duy nhất
- Bảo mật theo chuẩn công nghiệp: JWT + bcrypt + RBAC
- Đảm bảo tính toàn vẹn dữ liệu qua ràng buộc DB và kiểm tra nghiệp vụ ở service layer
- Viết unit test và integration test đầy đủ (pytest + httpx)

---

## 3. Target Users

### Ba vai trò chính trong hệ thống

```
+------------------------------------------------------------------+
|                       HE THONG THU VIEN                         |
|                                                                  |
|  DOC GIA (Reader)     THU THU (Librarian)   QUAN TRI (Admin)    |
|                                                                  |
|  - Tim & duyet sach   - Cap phat sach       - Quan ly kho sach  |
|  - Xem phieu muon     - Xu ly tra sach      - Quan ly the loai  |
|  - Gia han sach       - Theo doi phieu      - Quan ly nguoi dung |
|  - Danh gia sach      - Thu phi phat        - Dashboard thong ke |
|  - Quan ly ho so                            - Sync qua han       |
+------------------------------------------------------------------+
```

| Vai trò | Đối tượng thực tế | Nhu cầu chính |
|---|---|---|
| **Độc giả** | Sinh viên, thành viên thư viện | Tìm sách nhanh, tự phục vụ gia hạn, biết hạn trả |
| **Thủ thư** | Nhân viên quầy thư viện | Cấp phát/trả sách nhanh, tính phạt chính xác, không nhầm lẫn |
| **Admin** | Quản lý thư viện | Báo cáo tổng hợp, kiểm soát nhân sự và kho sách |

---

## 4. Technology Stack

### Tổng quan công nghệ theo tầng

```
+---------------------------------------------+
|           PRESENTATION LAYER                |
|  TailwindCSS  HTMX  Alpine.js  Chart.js     |
+---------------------------------------------+
|           APPLICATION LAYER                 |
|      Python 3.12   FastAPI   Jinja2         |
+---------------------------------------------+
|            SECURITY LAYER                   |
|        PyJWT   bcrypt   Pydantic v2         |
+---------------------------------------------+
|              DATA LAYER                     |
|     SQLAlchemy 2.x Async   aiosqlite        |
+---------------------------------------------+
|               DATABASE                      |
|            SQLite (library.db)              |
+---------------------------------------------+
```

### Giải thích từng công nghệ

#### Backend Core

| Công nghệ | Lý do chọn | Vai trò trong hệ thống |
|---|---|---|
| **Python 3.12** | Ngôn ngữ phổ biến, cú pháp rõ ràng, hệ sinh thái phong phú | Ngôn ngữ lập trình toàn bộ backend |
| **FastAPI** | Async native, tự động sinh API docs, type-safe với Pydantic | Framework chính — phục vụ cả REST API lẫn Web UI |
| **Uvicorn** | ASGI server hiệu năng cao, tương thích FastAPI | Chạy ứng dụng trong môi trường development và production |

#### Database & ORM

| Công nghệ | Lý do chọn | Vai trò trong hệ thống |
|---|---|---|
| **SQLite** | Nhẹ, không cần cài server, phù hợp đồ án | Lưu trữ toàn bộ dữ liệu trong 1 file `library.db` |
| **SQLAlchemy 2.x** | ORM mạnh nhất cho Python, hỗ trợ async | Ánh xạ Python class ↔ bảng DB, viết query Pythonic |
| **Alembic** | Migration chính thức của SQLAlchemy | Quản lý phiên bản schema, rollback an toàn |

#### Bảo mật & Xác thực

| Công nghệ | Lý do chọn | Vai trò trong hệ thống |
|---|---|---|
| **PyJWT** | Chuẩn JWT phổ biến nhất cho Python | Tạo/xác thực access token và refresh token |
| **bcrypt** | Thuật toán hash mật khẩu, chống brute-force | Hash mật khẩu người dùng — không lưu mật khẩu gốc |
| **Pydantic v2** | Validation mạnh, tích hợp sẵn FastAPI | Validate toàn bộ request/response, tạo API schema tự động |

#### Frontend & UI

| Công nghệ | Lý do chọn | Vai trò trong hệ thống |
|---|---|---|
| **Jinja2** | Template engine chuẩn Python, tích hợp sẵn FastAPI | Render HTML phía server (SSR) — không cần SPA framework |
| **HTMX** | Thêm tính năng dynamic vào HTML thuần, không cần nhiều JS | Live search, cập nhật bảng/danh sách không reload trang |
| **Alpine.js** | Reactivity nhẹ (~15kB), khai báo trực tiếp trong HTML | Dropdown, sidebar toggle, UI state nhỏ |
| **TailwindCSS** | CSS utility-first, responsive sẵn | Styling toàn bộ giao diện |
| **Chart.js** | Thư viện biểu đồ phổ biến, dễ tích hợp | Biểu đồ cột mượn/trả theo tháng trên admin dashboard |

#### Testing & Dev Tools

| Công nghệ | Lý do chọn | Vai trò trong hệ thống |
|---|---|---|
| **pytest + pytest-asyncio** | Framework test tiêu chuẩn Python, hỗ trợ async | Unit test và integration test toàn bộ API |
| **httpx** | HTTP client async — thay thế requests trong async | Gọi API trong integration tests |
| **Ruff** | Linter/formatter nhanh nhất cho Python | Đảm bảo chất lượng và nhất quán code style |

---

## 5. System Architecture Overview

### Kiến trúc Monolith Full-stack

Hệ thống được thiết kế theo mô hình **Monolith Full-stack** — một ứng dụng FastAPI duy nhất phục vụ cả hai giao diện:

```
                 [Trinh duyet Web]
                        |
           +------------+------------+
           |                         |
   [Web UI Routes]           [REST API Routes]
   Jinja2 SSR + HTMX          /api/v1/* (JSON)
   Cookie Auth                 Bearer Token Auth
           |                         |
           +------------+------------+
                        |
               [FastAPI Application]
                 (create_app())
                        |
           +------------+------------+
           |            |            |
      [Services]  [Middleware]  [Dependencies]
      Business     Access Log    JWT + RBAC
       Logic
           |
     [Repositories]
     Async DB Queries
           |
        [Models]
      ORM Entities
           |
  [SQLite -- library.db]
```

### Pattern 4 tầng (Layered Architecture)

| Tầng | Thành phần | Trách nhiệm |
|---|---|---|
| **Presentation** | `api/v1/` · `web/` · `templates/` | Tiếp nhận request, validate input, trả response/HTML |
| **Business Logic** | `services/` | Kiểm tra quy tắc nghiệp vụ, điều phối thao tác DB |
| **Data Access** | `repositories/` | Truy vấn database async — tách biệt khỏi business logic |
| **Data** | `models/` · SQLite | ORM entities, schema DB, constraint toàn vẹn dữ liệu |

### Dual Authentication

```
REST API Client         Web Browser
      |                      |
Bearer Token (JWT)    httponly Cookie (JWT)
      |                      |
 get_current_user()   get_current_web_user()
      |                      |
      +----------+-----------+
                 |
          require_role()
    (Reader / Librarian / Admin)
```

---

## 6. Database Design Summary

### 5 Entities cốt lõi

| Entity | Bảng | Mô tả | Trường quan trọng |
|---|---|---|---|
| **User** | `users` | Người dùng hệ thống | role (reader/librarian/admin), status (active/inactive) |
| **Book** | `books` | Đầu sách trong kho | quantity, available_quantity, status (Có sẵn/Hư hỏng/Mất) |
| **Category** | `categories` | Thể loại sách | name (unique) |
| **Borrowing** | `borrowings` | Phiếu mượn sách | status (borrowed/returned/overdue), fine_amount, fine_paid |
| **Review** | `reviews` | Đánh giá sách | rating (1–5), unique(user_id, book_id) |

### Thiết kế tồn kho kép

Bảng `books` dùng **hai trường số lượng** để phân biệt rõ:

```
quantity           = Tong so ban sach thu vien so huu
available_quantity = So ban hien co the muon

available_quantity = quantity - (so phieu dang BORROWED/OVERDUE)

Khi cap phat:  available_quantity -= 1
Khi tra:       available_quantity += 1
```

### Cơ chế phí phạt

```
fine_amount = days_overdue x FINE_PER_DAY (5.000 VND)

days_overdue = (ngay_hom_nay - due_date).days   [neu chua tra]
             = (return_date - due_date).days     [khi tra]

fine_paid = False  -->  chua thu
fine_paid = True   -->  da thu (thu thu xac nhan)
```

---

## 7. ERD Description

### Sơ đồ quan hệ

```
CATEGORIES (1) -------- (0..N) BOOKS
  |
  category_id FK (SET NULL)
  Xoa the loai: sach van ton tai, category_id = NULL

USERS (1) ------------- (0..N) BORROWINGS
  |
  user_id FK (RESTRICT)
  Khong xoa user con phieu muon

BOOKS (1) ------------- (0..N) BORROWINGS
  |
  book_id FK (RESTRICT)
  Khong xoa sach con phieu muon

USERS (1) ------------- (0..N) REVIEWS
  |
  user_id FK (CASCADE)
  Xoa user: xoa toan bo reviews cua user

BOOKS (1) ------------- (0..N) REVIEWS
  |
  book_id FK (CASCADE)
  Xoa sach: xoa toan bo reviews cua sach
```

### Ràng buộc quan trọng

| Ràng buộc | Loại | Ý nghĩa nghiệp vụ |
|---|---|---|
| `users.username` UNIQUE | DB Constraint | Không trùng tên đăng nhập |
| `users.email` UNIQUE | DB Constraint | Không trùng email |
| `books.isbn` UNIQUE | DB Constraint | Mỗi đầu sách có ISBN riêng |
| `reviews(user_id, book_id)` UNIQUE | DB Constraint | Mỗi reader chỉ review 1 lần/sách |
| `borrowings.user_id` RESTRICT | FK Constraint | Bảo vệ lịch sử mượn khi xóa user |
| `borrowings.book_id` RESTRICT | FK Constraint | Bảo vệ phiếu mượn khi xóa sách |

---

## 8. Business Logic Flow

### Luồng 1: Cấp phát sách (Issue Book)

```
THU THU
  |
  +-- 1. Tim kiem reader (live search HTMX)
  +-- 2. Tim kiem sach (live search HTMX)
  +-- 3. Thiet lap ngay tra (tuy chon, mac dinh +14 ngay)
  +-- 4. Nhan "Cap phat"
              |
              v
       [BorrowingService.issue_book()]
              |
       Kiem tra 5 dieu kien:
       [v] Reader active?
       [v] Sach ton tai?
       [v] available_quantity > 0?
       [v] Reader < 5 phieu active?
       [v] Reader chua muon sach nay?
              |
         +----+----+
       FAIL       PASS
         |           |
     Loi 422     Tao Borrowing
                 available_quantity -= 1
```

### Luồng 2: Trả sách (Return Book)

```
THU THU
  |
  +-- 1. Chon phieu muon can xu ly
  +-- 2. Ghi nhan tinh trang sach (good/fair/poor/damaged)
  +-- 3. Nhan "Xac nhan tra"
              |
              v
       [BorrowingService.return_book()]
              |
       Tinh phi phat:
       fine = days_overdue x 5.000 VND
              |
       Cap nhat:
       status       --> RETURNED
       return_date  --> hom nay
       fine_amount  --> fine
       available_quantity += 1
              |
       [Sau do] Thu thu thu tien phat
       --> mark_fine_paid() --> fine_paid = True
```

### Luồng 3: Gia hạn (Renew)

```
READER hoac THU THU
  |
  +--> Yeu cau gia han phieu muon
              |
              v
       [BorrowingService.renew_borrowing()]
              |
       Kiem tra:
       [v] status == BORROWED?
       [v] renewed_count < 2?
              |
         +----+----+
       FAIL       PASS
         |           |
     Loi 409/422  due_date += 14 ngay
                  renewed_count += 1
```

### Luồng 4: Đánh giá sách

```
READER
  |
  +--> Gui danh gia (rating + comment)
              |
              v
       [ReviewService]
              |
       Kiem tra:
       [v] Reader da tung muon sach nay?
       [v] Chua co review cho cap (user, book)?
              |
           PASS --> Luu Review (rating 1-5 + comment)
```

### Luồng 5: Đồng bộ quá hạn

```
ADMIN
  |
  +--> Kich hoat Sync (Web UI button hoac API)
              |
              v
       [BorrowingService.sync_overdue_statuses()]
              |
       Quet tat ca borrowing:
       status in {BORROWED, OVERDUE} & due_date < hom nay
              |
       Voi moi phieu qua han:
       status      --> OVERDUE
       fine_amount --> days_overdue x 5.000 VND
              |
       Tra ve: so phieu da cap nhat
```

---

## 9. Roles & Permissions Summary

### Phân cấp vai trò

```
ADMIN  >  LIBRARIAN  >  READER
```

_Admin có tất cả quyền của Librarian và Reader_

### Tóm tắt quyền theo nhóm

| Nhóm chức năng | Reader | Librarian | Admin |
|---|:---:|:---:|:---:|
| **Truy cập public** (không cần login) | ✓ | ✓ | ✓ |
| **Tự phục vụ** (xem phiếu, gia hạn, đánh giá) | ✓ | ✓ | ✓ |
| **Lưu thông sách** (cấp phát, trả, thu phạt) | — | ✓ | ✓ |
| **Quản lý kho sách & thể loại** | — | — | ✓ |
| **Quản lý người dùng** | — | — | ✓ |
| **Dashboard & báo cáo** | — | — | ✓ |

### Cơ chế bảo mật

- **RBAC** được enforce ở 2 lớp: FastAPI Dependency Injection (API) và Web route (Cookie)
- **Reader isolation**: Reader chỉ thấy dữ liệu của bản thân — kiểm tra ở cả service layer lẫn DB query
- **Token duality**: REST API dùng Bearer Token trong `Authorization` header; Web UI dùng httponly Cookie (không thể đọc bằng JavaScript)
- **Account deactivation**: `status=INACTIVE` bị chặn đăng nhập ngay tại AuthService

---

## 10. Functional Overview

### Module 1 — Kho Sách (Book Catalog)

> Quản lý toàn bộ danh mục sách và thể loại

- Thêm/sửa/xóa sách với đầy đủ thông tin (ISBN, tác giả, NXB, năm, ngôn ngữ, mô tả)
- Upload và hiển thị ảnh bìa sách (đặt tên file theo ISBN)
- Quản lý thể loại sách — CRUD inline không reload trang (HTMX)
- Tìm kiếm full-text (tựa sách / tác giả / ISBN) + lọc đa điều kiện
- Theo dõi tồn kho: tổng số bản / số bản có sẵn / trạng thái vật lý

### Module 2 — Lưu Thông Sách (Circulation)

> Toàn bộ quy trình mượn và trả sách

- **Cấp phát:** Live search reader + sách bằng HTMX, kiểm tra 5 điều kiện nghiệp vụ
- **Trả sách:** Ghi nhận tình trạng, tự động tính phí phạt theo ngày quá hạn
- **Gia hạn:** Tối đa 2 lần, mỗi lần +14 ngày, kiểm tra điều kiện tự động
- **Phí phạt:** Theo dõi fine_amount và fine_paid; thủ thư xác nhận sau khi thu tiền
- **Sync quá hạn:** Cập nhật hàng loạt trạng thái OVERDUE khi được kích hoạt

### Module 3 — Tự Phục Vụ Độc Giả (Reader Self-Service)

> Độc giả tự quản lý hoạt động mượn sách của mình

- Xem danh sách sách đang mượn với trạng thái và hạn trả
- Gia hạn sách tự phục vụ (không cần ra quầy thủ thư)
- Xem toàn bộ lịch sử mượn/trả với phân trang
- Cập nhật hồ sơ cá nhân và đổi mật khẩu
- Viết đánh giá sách (1–5 sao + nhận xét, điều kiện: đã từng mượn)

### Module 4 — Dashboard & Thống Kê (Analytics)

> Tổng hợp dữ liệu hoạt động cho ban quản lý

- **KPI Cards:** Tổng sách · Tổng độc giả · Phiếu đang mượn · Phiếu quá hạn · Tiền phạt thu được / chưa thu
- **Biểu đồ Chart.js:** Số lượng cấp phát và trả sách theo từng tháng trong năm
- **Top 5 sách phổ biến:** Xếp hạng theo số lượt mượn
- **Top 5 độc giả tích cực:** Xếp hạng theo số lượt mượn
- **Bảng tồn kho:** Danh sách sách sắp theo số bản có sẵn (ít nhất lên trên)

### Module 5 — REST API & Tích hợp (API Layer)

> Giao diện lập trình cho client và tích hợp bên ngoài

- JSON API đầy đủ tại `/api/v1/` — cover 100% chức năng hệ thống
- Swagger UI tự động tại `/api/docs` (sinh từ Pydantic schema + FastAPI)
- OAuth2 Password Flow cho lấy token (`POST /api/v1/auth/login`)
- Phân trang chuẩn hóa với `PaginatedResponse[T]` generic cho mọi danh sách

---

## 11. User Journey

### Hành trình Độc Giả (Reader Journey)

```
[Lần đầu - không cần login]
Truy cập trang chủ
  --> Duyệt sách / Tìm kiếm / Lọc
  --> Xem chi tiết sách + đánh giá cộng đồng
  --> Đăng ký tài khoản
  --> Đăng nhập

[Sau khi mượn sách (qua thủ thư)]
Vào trang "Sách đang mượn"
  --> Xem danh sách phiếu + hạn trả
  --> Gia hạn (nếu cần, tối đa 2 lần)
  --> [Sau khi trả] Viết đánh giá sách
```

### Hành trình Thủ Thư (Librarian Journey)

```
Đăng nhập
  --> Trang "Cấp phát sách"
        --> Gõ tên reader --> live search (HTMX)
        --> Gõ tên sách   --> live search (HTMX)
        --> Chọn ngày trả --> Xác nhận cấp phát
  --> Trang "Quản lý phiếu mượn"
        --> Lọc: borrowed / overdue / returned
        --> Chọn phiếu --> Xử lý trả sách
              --> Ghi tình trạng sách
              --> Hệ thống hiển thị phí phạt tự tính
              --> Xác nhận trả
        --> Thu tiền phạt --> Mark fine paid
```

### Hành trình Admin (Admin Journey)

```
Đăng nhập
  --> Dashboard
        --> Xem KPI tổng quan
        --> Xem biểu đồ mượn/trả theo tháng
        --> Xem top 5 sách / top 5 độc giả
  --> Quản lý sách
        --> Thêm sách mới (upload ảnh bìa)
        --> Sửa thông tin / số lượng bản
  --> Quản lý thể loại
        --> Thêm/sửa/xóa inline (không reload)
  --> Quản lý người dùng
        --> Đổi role / activate / deactivate / xóa
  --> Sync trạng thái quá hạn
        --> Nhấn Sync --> hệ thống cập nhật hàng loạt
```

---

## 12. System Limitations

> Chỉ liệt kê hạn chế thực sự thấy được từ implementation.

### Giới hạn kỹ thuật

| Hạn chế | Mô tả | Ảnh hưởng |
|---|---|---|
| **SQLite single-file** | Không hỗ trợ multi-writer concurrent tốt | Phù hợp thư viện quy mô nhỏ/vừa; cần PostgreSQL nếu scale |
| **Sync Overdue thủ công** | Không có cron job tự động chạy định kỳ | Admin phải nhấn nút thủ công để cập nhật trạng thái quá hạn |
| **Không có email notification** | Không gửi email nhắc nhở hạn trả | Reader không nhận cảnh báo khi sắp đến hạn |
| **Single server Monolith** | Không có horizontal scaling | Không load balancing, không container orchestration |
| **Cover image local storage** | Ảnh bìa lưu trên disk server | Không CDN, mất file nếu server bị reset |

### Giới hạn tính năng

| Hạn chế | Mô tả |
|---|---|
| **Không có xác thực 2 bước** | Đăng ký và đổi mật khẩu không có OTP/email verify |
| **Không có tính năng đặt trước** | Reader không thể đặt chỗ sách đang hết |
| **Không tích hợp barcode** | Cấp phát/trả sách nhập tay, không có máy quét mã vạch |
| **Báo cáo cơ bản** | Không export PDF/Excel, chỉ xem trên web |
| **Refresh token chưa có revoke list** | Đăng xuất không vô hiệu hoá token cũ ngay lập tức |

---

## 13. Recommended Presentation Story Flow

### Cấu trúc 10 slide — thứ tự logic từ WHY đến HOW đến WHAT

```
SLIDE 1 -- Gioi thieu de tai
  Van de thu vien truyen thong --> Giai phap so hoa
  Hook: "Tu so sach giay den ung dung web Python"

SLIDE 2 -- Muc tieu he thong
  5 muc tieu chuc nang cu the, do luong duoc
  Transition: "De dat duoc muc tieu do, chung ta dung gi?"

SLIDE 3 -- Cong nghe su dung
  Tech stack theo tang, giai thich ly do chon moi cong nghe
  Focus: Python + FastAPI la trung tam

SLIDE 4 -- Tong quan kien truc
  So do Monolith Full-stack, Pattern 4 tang, Dual Auth
  Transition: "He thong duoc to chuc nhu the nao?"

SLIDE 5 -- Cau truc du an
  Folder tree, module chinh va vai tro tung tang
  Transition: "Du lieu duoc thiet ke ra sao?"

SLIDE 6 -- ERD & Thiet ke CSDL
  5 entities, quan he, ton kho kep, co che phi phat
  Transition: "Nghiep vu van hanh nhu the nao?"

SLIDE 7 -- Business Logic Flow
  3 luong chinh: Cap phat --> Tra --> Gia han (flowchart)
  Focus: diem kiem tra nghiep vu, tu dong hoa phi phat

SLIDE 8 -- Roles & Phan quyen
  Ma tran phan quyen 3 vai tro, co che RBAC + dual auth
  Transition: "He thong co nhung tinh nang gi?"

SLIDE 9 -- Chuc nang & Giao dien
  Screenshots giao dien thuc te theo tung module
  Demo: Live search HTMX, Dashboard Chart.js, Admin panel

SLIDE 10 -- Ket luan, Han che & Huong phat trien
  Tong ket ket qua, han che thuc te, cai tien tuong lai
  Ket: Q&A
```

### Điểm nhấn khi trình bày

1. **Mở đầu bằng vấn đề thực tế** — đừng bắt đầu bằng kỹ thuật
2. **Giải thích lý do chọn công nghệ** — không chỉ liệt kê tên
3. **Dùng sơ đồ kiến trúc** — người nghe thấy được bức tranh toàn cảnh
4. **Luồng nghiệp vụ bằng flowchart** — dễ hiểu hơn bảng chữ
5. **Demo giao diện thực tế** — slide 9 nên có screenshots hoặc video ngắn
6. **Hạn chế — trình bày tự tin** — thể hiện sự hiểu rõ phạm vi dự án
7. **Kết bằng hướng phát triển** — cho thấy tư duy mở rộng
