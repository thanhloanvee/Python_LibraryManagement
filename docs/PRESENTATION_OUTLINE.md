# PRESENTATION_OUTLINE.md — Library Management System
## Phase 3 Part B: Slide Comparison & Final Presentation Outline

---

## 1. Coverage Analysis

### So sánh File A (16 slides) và File B (10 slides) với tài liệu phân tích

| Chủ đề cần trình bày | File A | File B | Đánh giá |
|---|---|---|---|
| Giới thiệu đề tài / bài toán | Slide 2 | Slide 1–2 | Có, đủ nội dung |
| Mục tiêu hệ thống | Slide 2 (gộp) | Slide 2 | Mờ nhạt — thiếu bảng mục tiêu rõ ràng |
| Công nghệ sử dụng | Slide 4 | Slide 3 | File A thiếu HTMX, Alpine.js, TailwindCSS, Chart.js, Ruff |
| Kiến trúc hệ thống | Slide 5–6 | Slide 4 | Có, nhưng Slide 6 (MVC) dư thừa — không cần thiết |
| Cấu trúc dự án | Slide 7 | Slide 4 (gộp) | File A có riêng; File B gộp vào kiến trúc |
| ERD & Thiết kế CSDL | Slide 8 | Slide 6 | Có; thiếu bảng `categories`; thiếu ON DELETE strategy |
| Business Logic Flow | Slide 9 (một phần) | Slide 7 | Cả hai chỉ list bước — thiếu diagram flow có trực quan |
| Roles & Phân quyền | Slide 10 | Slide 8 | Có; File A đầy đủ hơn |
| Chức năng & Giao diện | Slide 3, 12 | Slide 9 | Slide 3 list features; Slide 12 UI mock — thiếu screenshot thực |
| Hạn chế hệ thống | Slide 13 | Slide 10 (gộp) | Có; File A có điểm sai (Soft Delete — thực tế DB dùng RESTRICT) |
| Hướng phát triển | Slide 14 | Slide 10 | Có |
| Kết luận | Slide 15 | Slide 10 | Có |

---

## 2. Missing Presentation Content

### Chủ đề hoàn toàn thiếu

| # | Nội dung thiếu | Vị trí nên thêm |
|---|---|---|
| 1 | **HTMX live search** — tính năng UX nổi bật nhất, không xuất hiện trong File A | Slide Công nghệ + Slide Demo |
| 2 | **Dual interface** — cùng 1 server phục vụ cả Web UI (/web/*) lẫn REST API (/api/v1/) với 2 auth mechanism khác nhau (cookie vs Bearer) | Slide Kiến trúc |
| 3 | **User Journey** — luồng tương tác đầu từ đầu đến cuối của từng vai trò (Reader, Librarian, Admin) | Slide Business Logic |
| 4 | **Bảng categories trong ERD** — toàn bộ File A bỏ sót entity này | Slide ERD |
| 5 | **ON DELETE strategy** — SET NULL / RESTRICT / CASCADE — minh chứng cho data integrity | Slide ERD |
| 6 | **Sync overdue workflow** — Admin kích hoạt thủ công, logic tính phạt tích lũy | Slide Business Logic |
| 7 | **Screenshot thực tế** — cả hai file dùng mock data; không có screenshot thật từ app | Slide Demo / Giao diện |
| 8 | **Dual auth mechanism** — JWT httponly cookie (Web) vs Bearer token (API) | Slide Bảo mật |

### Nội dung sai hoặc thiếu chính xác trong slide hiện tại

| # | Slide | Vấn đề |
|---|---|---|
| 1 | File A — Slide 13 | "No Soft Delete — Deleting a book with active borrows can cause data integrity errors" — **SAI**: DB dùng `RESTRICT` constraint, hệ thống **chặn** xóa sách khi còn phiếu active; không gây lỗi integrity |
| 2 | File A — Slide 4 | Thiếu HTMX, Alpine.js, TailwindCSS, Chart.js — là các công nghệ frontend quan trọng |
| 3 | File A — Slide 9 | Borrow API list endpoint `/books` ghi "Librarian+" nhưng thực tế là **Public** |
| 4 | File B — Slide 7 | "Reader requests" renewal — thực ra Reader tự gia hạn trực tiếp, không "request" |

---

## 3. Recommended Slide Improvements

### File A — Những slide nên sửa

| Slide | Vấn đề | Hành động |
|---|---|---|
| Slide 3 (Chức năng chính) | Liệt kê dạng bảng module, thiếu context nghiệp vụ | Gộp vào Slide Mục tiêu hoặc Business Logic Flow |
| Slide 4 (Tech Stack) | Thiếu HTMX, Alpine.js, TailwindCSS, Chart.js, Ruff | Bổ sung frontend stack |
| Slide 5 (Kiến trúc) | Diagram text-only, không trực quan | Thay bằng diagram có layers rõ ràng |
| Slide 6 (MVC Pattern) | Nội dung trùng lặp với Slide 5 và 7; MVC không chính xác với kiến trúc thực (Layered, không phải MVC thuần) | **Xóa** hoặc gộp vào Slide Kiến trúc |
| Slide 8 (ERD) | Thiếu bảng `categories`; thiếu ON DELETE rules | Bổ sung đủ 5 entities và constraints |
| Slide 11 (Demo placeholder) | Slide trống | Thay bằng nội dung thực hoặc xóa |
| Slide 13 (Limitations) | Nội dung sai về Soft Delete | Sửa: "DB RESTRICT prevents deletion" thay vì "can cause errors" |

### Slide nên gộp

| Gộp | Lý do |
|---|---|
| Slide 5 + Slide 6 | Slide 5 (Architecture) đã bao gồm nội dung Slide 6 (MVC); gộp thành 1 slide Kiến trúc đầy đủ |
| Slide 11 + Slide 12 | Slide 11 là placeholder trống; gộp vào Slide Demo thực |
| Slide 3 + Slide 9 | Chức năng chính (Slide 3) và API Flow (Slide 9) cùng nói về features; tách theo góc nhìn (business vs technical) |

### Slide nên tách

| Tách | Lý do |
|---|---|
| Slide 2 (Giới thiệu + Mục tiêu) | Quá nhiều nội dung; tách thành Slide 1 (Giới thiệu bài toán) và Slide 2 (Mục tiêu + phạm vi) |

---

## 4. Recommended New Slides

| Slide mới | Nội dung | Lý do cần thiết |
|---|---|---|
| **User Journey** | Sơ đồ 3 hành trình: Reader → Librarian → Admin với các bước cụ thể | Giúp hội đồng hiểu hệ thống từ góc nhìn người dùng thực tế |
| **HTMX Demo context** | Giải thích HTMX partial update; minh họa live search without SPA | Tính năng kỹ thuật đặc sắc nhất, chưa được đề cập |

---

## 5. Recommended Visuals

| Slide | Visual đề xuất |
|---|---|
| Giới thiệu đề tài | Before/After: Sổ giấy thủ công → Web interface |
| Công nghệ | Tech stack diagram phân layer (Frontend / Backend / DB) |
| Kiến trúc | Layered architecture diagram: Browser → FastAPI → Services → Repo → SQLite |
| ERD | Sơ đồ ERD với 5 bảng và đường quan hệ có nhãn cardinality |
| Business Logic Flow | Flowchart mượn sách với 5 điểm kiểm tra (diamond shapes) |
| Roles & Phân quyền | Ma trận quyền dạng bảng màu (xanh = có, đỏ = không) |
| Demo / Giao diện | Screenshot thực: Dashboard, Issue form với live search, Book list |
| Kết luận | Timeline roadmap 3 giai đoạn |

---

## 6. Final Presentation Outline — 10 Slides

> Target: 10 slides · Ngôn ngữ: Tiếng Việt (nội dung chính) + English (thuật ngữ kỹ thuật)

---

### Slide 1 — Giới thiệu đề tài

**Objective:** Đặt bài toán thực tế và giới thiệu giải pháp số hoá.

**Key Bullets:**
- Thư viện truyền thống: quản lý sổ giấy → khó kiểm soát, dễ sai sót
- Giải pháp: Hệ thống LMS trực tuyến — số hoá toàn bộ quy trình
- Dự án tái viết từ PHP/Yii2 → Python/FastAPI hiện đại
- Vừa là Web App hoàn chỉnh, vừa là REST API có thể tích hợp
- Nhóm: Lê Thị Thanh Loan (24210228) · Trần Hưng Khoa (24210220)

**Suggested Visual:** Split-screen — bên trái: hình ảnh sổ sách thủ công; bên phải: screenshot trang chủ LMS web app

**Speaker Notes:**
> Mở đầu bằng bài toán thực tế — thư viện phải ghi chép bằng tay, không biết sách nào đang được mượn, ai đang giữ, sách nào quá hạn. Hệ thống này giải quyết trọn vẹn bài toán đó. Đặc biệt, đây không chỉ là migration công nghệ mà là một rewrite hoàn toàn, giữ nguyên nghiệp vụ nhưng nâng cấp toàn bộ nền tảng kỹ thuật.

---

### Slide 2 — Mục tiêu hệ thống

**Objective:** Trình bày rõ 6 mục tiêu cốt lõi và phạm vi hệ thống.

**Key Bullets:**
- Số hoá phiếu mượn/trả — thay thế sổ giấy
- Kiểm soát tồn kho real-time (`available_quantity` cập nhật ngay)
- Tự động tính phí phạt: `days_overdue × 5,000 VND`
- Phân quyền rõ ràng — RBAC 3 cấp: Reader / Librarian / Admin
- Dashboard thống kê — KPI, biểu đồ tháng, top sách/độc giả
- REST API đầy đủ — sẵn sàng tích hợp mobile / third-party

**Suggested Visual:** Bảng mục tiêu 2 cột: Mục tiêu | Giải pháp trong hệ thống (lấy từ DESIGN_DOC Section 2)

**Speaker Notes:**
> Mỗi mục tiêu đều được "mã hoá" trực tiếp vào business rules trong code — không chỉ là lý thuyết. Ví dụ: tự động tính phạt được implement trong `BorrowingService.calculate_fine()`, giới hạn 5 phiếu/reader được enforce trong `issue_book()`. Nêu phạm vi: không bao gồm thanh toán online, reservation, hay mobile app — những thứ này là future work.

---

### Slide 3 — Công nghệ sử dụng

**Objective:** Giới thiệu toàn bộ tech stack phân theo layer, giải thích lý do chọn.

**Key Bullets:**
- **Backend:** Python 3.12 + FastAPI (async-native, auto OpenAPI docs) + Uvicorn
- **Database:** SQLite + SQLAlchemy 2.x async ORM + Alembic migrations
- **Frontend:** Jinja2 SSR + HTMX (partial updates) + Alpine.js + TailwindCSS + Chart.js
- **Security:** PyJWT + bcrypt + Pydantic v2 validation
- **Dev Tools:** pytest + pytest-asyncio + httpx + Ruff

**Suggested Visual:** Layer diagram (5 tầng màu sắc khác nhau): Frontend → Web Server → Business Layer → Data Layer → Database; mỗi tầng liệt kê tên tech tương ứng

**Speaker Notes:**
> Điểm đáng chú ý: cùng 1 FastAPI server phục vụ cả Web UI (Jinja2 SSR) và REST API (JSON) — không cần 2 server riêng biệt. HTMX là lựa chọn thay thế SPA (React/Vue) — giữ được SSR đơn giản mà vẫn có UX phản hồi tức thì (live search, inline edit). Nếu hội đồng hỏi "tại sao không dùng React?" — trả lời: HTMX phù hợp hơn với server-centric architecture, không cần build pipeline riêng.

---

### Slide 4 — Tổng quan kiến trúc hệ thống

**Objective:** Trình bày Monolith Full-stack architecture, luồng request, và dual interface.

**Key Bullets:**
- Kiến trúc: **Monolith Full-stack** — 1 FastAPI server, 2 giao diện
- **Web UI** (`/`, `/books`, `/admin/*`, `/reader/*`) → auth via httponly cookie
- **REST API** (`/api/v1/*`) → auth via Bearer JWT token + Swagger UI
- Layered: Router → Service (business logic) → Repository (DB queries) → SQLite
- Dependency Injection: FastAPI DI quản lý DB session, auth, RBAC

**Suggested Visual:** Architecture diagram dọc: Browser ↔ [Web UI / REST API] ↔ Services ↔ Repositories ↔ SQLite; với chú thích "httponly cookie" và "Bearer JWT" ở hai nhánh

**Speaker Notes:**
> Điểm kỹ thuật quan trọng: 2 interface trên cùng 1 server với 2 cơ chế auth khác nhau. Web dùng cookie để tránh XSS (httponly), API dùng Bearer token cho programmatic access. Service layer là trung tâm — toàn bộ business rules nằm ở đây, không rải rác trong routes. Repository chỉ thuần query DB, không có logic nghiệp vụ.

---

### Slide 5 — Cấu trúc dự án

**Objective:** Giải thích tổ chức thư mục và vai trò từng package chính.

**Key Bullets:**
- `models/` — 5 SQLAlchemy ORM entities (User, Book, Category, Borrowing, Review)
- `schemas/` — Pydantic v2 DTOs: validate input, serialize output
- `repositories/` — Data access layer: async DB queries, không có business logic
- `services/` — Business logic layer: BorrowingService, AuthService, DashboardService
- `api/v1/` + `web/` — REST endpoints (JSON) + Web UI endpoints (HTML)
- `dependencies/` — `auth.py` (JWT decode) + `rbac.py` (role enforcement)

**Suggested Visual:** Directory tree diagram với 2 màu: xanh = layer logic, cam = infrastructure; hoặc dạng card từng module với tên file ví dụ

**Speaker Notes:**
> Nguyên tắc thiết kế: mỗi layer có trách nhiệm duy nhất. Nếu hội đồng hỏi "tại sao cần cả Service lẫn Repository?" — giải thích: Repository chỉ biết "lấy data thế nào", Service mới biết "khi nào được lấy và làm gì với data đó". Ví dụ: `BorrowingRepository` chỉ query DB, còn `BorrowingService` kiểm tra 5 điều kiện trước khi gọi repository.

---

### Slide 6 — ERD & Thiết kế cơ sở dữ liệu

**Objective:** Trình bày 5 entity, quan hệ, và chiến lược toàn vẹn dữ liệu.

**Key Bullets:**
- 5 bảng: `users` · `categories` · `books` · `borrowings` · `reviews`
- Trường đặc biệt: `available_quantity` (cập nhật real-time), `fine_amount`, `renewed_count`
- Ràng buộc ON DELETE: `RESTRICT` (user/book → borrowings), `CASCADE` (user/book → reviews), `SET NULL` (category → books)
- Unique constraint: `(user_id, book_id)` trên `reviews` — mỗi reader chỉ review 1 lần/sách
- Migration: Alembic `001_initial_schema.py`

**Suggested Visual:** ERD diagram đầy đủ 5 bảng với cardinality (1–N), tên cột chính, và mũi tên ON DELETE được tô màu (đỏ = RESTRICT, xanh = CASCADE, xám = SET NULL)

**Speaker Notes:**
> Điểm cần nhấn: `RESTRICT` trên borrowings bảo vệ lịch sử dữ liệu — không thể xóa user hay sách khi còn phiếu mượn. Đây là data integrity được enforce ở tầng DB, không chỉ ở code. `available_quantity` tách biệt với `quantity` (tổng bản nhập) để tracking real-time mà không cần count phiếu mượn mỗi lần query.

---

### Slide 7 — Business Logic Flow

**Objective:** Trình bày chi tiết 2 luồng nghiệp vụ cốt lõi: mượn và trả sách.

**Key Bullets:**
- **Mượn sách (Issue):** 5 kiểm tra tuần tự → tạo phiếu → `available_quantity -= 1`
  - ✓ Reader tồn tại & active · ✓ Sách tồn tại · ✓ `available_quantity > 0` · ✓ Reader < 5 phiếu active · ✓ Reader chưa mượn sách này
- **Trả sách (Return):** Ghi tình trạng → tính phạt tự động → `available_quantity += 1` → thu phạt
  - `fine_amount = (return_date − due_date) × 5,000 VND`
- **Gia hạn (Renew):** Tối đa 2 lần · `due_date += 14 ngày` · `renewed_count += 1`
- **Sync overdue:** Admin kích hoạt → tất cả phiếu quá hạn được cập nhật status + tính lại fine

**Suggested Visual:** Flowchart dọc luồng mượn sách với 5 diamond (điều kiện) màu đỏ/xanh; bên cạnh là mini-flowchart luồng trả sách

**Speaker Notes:**
> Đây là core business logic — mỗi validation check trong `BorrowingService.issue_book()` tương ứng với 1 quy tắc nghiệp vụ thực tế. Demo luồng này trực tiếp trên form `/admin/borrowings/issue` sẽ rất ấn tượng — nhập reader, nhập sách, hệ thống tự kiểm tra và báo lỗi cụ thể nếu vi phạm rule.

---

### Slide 8 — Roles & Phân quyền

**Objective:** Trình bày RBAC 3 cấp, ma trận quyền, và cách enforce trong code.

**Key Bullets:**
- **3 roles:** Reader (độc giả) · Librarian (thủ thư) · Admin (quản trị viên)
- **Public access** (chưa đăng nhập): Duyệt sách, xem chi tiết — không cần login
- **Enforce tại 2 tầng:** Web layer (cookie) + API layer (Bearer JWT) → cùng `rbac.py`
- **Quy tắc đặc biệt:** Reader tự đăng ký (chỉ role `reader`); tối đa 5 phiếu active; tối đa 2 lần gia hạn
- **Inactive account:** Không thể đăng nhập, bị chặn ngay tại `AuthService.login()`

**Suggested Visual:** Ma trận quyền dạng bảng màu: cột = Feature groups, hàng = Roles; ô xanh = có quyền, ô đỏ = không; thêm cột "Public" cho anonymous access

**Speaker Notes:**
> RBAC được enforce ở cả 2 layer — không chỉ ở UI. Nếu hội đồng hỏi "Reader có thể bypass bằng cách gọi API trực tiếp không?" — câu trả lời là không, vì `require_reader/librarian/admin` trong `dependencies/rbac.py` được inject vào cả API routes lẫn Web routes. Demo: thử gọi `POST /api/v1/borrowings` với Reader token → nhận 403.

---

### Slide 9 — Chức năng hệ thống & Giao diện

**Objective:** Demo các màn hình thực tế, nhóm theo 7 module chức năng.

**Key Bullets:**
- **Catalogue:** Trang chủ, danh sách sách (search + filter), chi tiết sách + reviews
- **Circulation:** Issue form (HTMX live search reader/book), Return form (auto fine calc), Renew
- **Admin Dashboard:** KPI cards · Biểu đồ mượn/trả theo tháng (Chart.js) · Top 5 sách/readers
- **Catalogue Management:** CRUD sách (upload ảnh bìa), CRUD thể loại (inline HTMX)
- **User Management:** Danh sách users, thay đổi role, khoá tài khoản
- **Reader Portal:** My Books, Lịch sử, Hồ sơ, Đổi mật khẩu
- **API Docs:** Swagger UI tại `/api/docs` — tự động từ FastAPI + Pydantic schemas

**Suggested Visual:** Screenshot grid 2×3: (1) Admin Dashboard với Chart.js, (2) Issue form live search, (3) Book list với search/filter, (4) Book detail + reviews, (5) Return form với fine display, (6) Swagger UI

**Speaker Notes:**
> Demo trực tiếp theo thứ tự: (1) trang chủ public, (2) issue form với HTMX live search — gõ tên reader/sách, kết quả hiện ngay không reload, (3) admin dashboard với Chart.js, (4) Swagger UI. Nếu không có thời gian demo thực, nhấn mạnh HTMX live search — đây là điểm kỹ thuật phân biệt hệ thống này với các giải pháp SSR thông thường.

---

### Slide 10 — Kết luận, Hạn chế & Hướng phát triển

**Objective:** Tổng kết thành quả, thừa nhận hạn chế thực tế, đề xuất roadmap.

**Key Bullets:**
- **Đã hoàn thành:** Full-stack Web App + REST API · RBAC 3 cấp · Circulation workflow (borrow/return/renew/fine) · Admin Dashboard + Chart.js · 18 test cases (auth, books, borrowings)
- **Hạn chế chính:** SQLite (phù hợp học thuật, không production-scale) · Sync overdue thủ công · Chưa có email notifications · Reader chưa tự mượn được
- **Hướng phát triển ngắn hạn:** PostgreSQL + APScheduler auto-sync · Rate limiting · Book reservation queue
- **Hướng phát triển dài hạn:** Mobile app (tận dụng REST API có sẵn) · Docker + CI/CD · AI recommendation · VNPay integration

**Suggested Visual:** 2 cột: bên trái "Đã làm được" (checkmark xanh), bên phải "Hướng phát triển" (arrow icon); phía dưới: timeline roadmap 3 giai đoạn ngắn/trung/dài hạn

**Speaker Notes:**
> Khi nói về hạn chế: không xin lỗi về SQLite — thay vào đó nêu "SQLite phù hợp với quy mô dự án học thuật và thư viện nhỏ; khi scale lên, chỉ cần đổi connection string sang PostgreSQL vì SQLAlchemy đã abstract database driver". Nhấn mạnh: REST API đã sẵn sàng — mobile app chỉ cần consume API, không cần viết lại backend.

---

## 7. Slide Reorder Rationale

```
Slide 1  — Giới thiệu đề tài       (Bài toán → Giải pháp → Context migration)
Slide 2  — Mục tiêu hệ thống       (6 mục tiêu cụ thể + phạm vi)
Slide 3  — Công nghệ sử dụng       (Full stack: tại sao chọn, vai trò từng tech)
Slide 4  — Kiến trúc hệ thống      (Monolith, dual interface, layered pattern)
Slide 5  — Cấu trúc dự án          (Directory + module roles)
Slide 6  — ERD & CSDL              (5 entities, relationships, constraints)
Slide 7  — Business Logic Flow     (Issue / Return / Renew / Sync flowchart)
Slide 8  — Roles & Phân quyền      (RBAC matrix, enforce mechanism)
Slide 9  — Chức năng & Giao diện   (Screenshots: 7 modules, HTMX demo)
Slide 10 — Kết luận & Hướng phát triển (Summary, limitations, roadmap)
```

**Logic trình bày:** Why (bài toán) → What (mục tiêu) → How/Tech (công nghệ + kiến trúc + cấu trúc) → Data (ERD) → Logic (business flow + RBAC) → Show (demo) → Reflect (kết luận)
