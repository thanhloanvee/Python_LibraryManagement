# PRESENTATION_OUTLINE.md — Hệ Thống Quản Lý Thư Viện
## Phase 3 Part B: Slide Comparison & Final Presentation Outline

---

## 1. Coverage Analysis

### File A (Python_LMS_Slides.pptx — 16 slides)

| Slide | Tiêu đề | Đánh giá |
|---|---|---|
| 1 | Cover / Title | Ổn — đầy đủ thông tin nhóm |
| 2 | Giới thiệu đề tài | Ổn — có problem, goals, target users |
| 3 | Chức năng chính | Ổn — liệt kê theo 4 module |
| 4 | Công nghệ sử dụng | Thiếu — không có HTMX, TailwindCSS, Alpine.js, Chart.js |
| 5 | Kiến trúc hệ thống | Ổn — nhưng thiếu dual auth, thiếu sơ đồ trực quan |
| 6 | Mô hình MVC | **Không chính xác** — hệ thống không theo MVC mà là Layered Architecture (4 tầng) |
| 7 | Tổ chức mã nguồn | Ổn — có folder tree và module roles |
| 8 | Data Model / ERD | Thiếu — không có Category entity, thiếu quan hệ ON DELETE, thiếu cơ chế tồn kho kép |
| 9 | Controller Layer / API Flow | Quá chi tiết kỹ thuật — liệt kê 10 bước internal + endpoint table |
| 10 | Bảo mật & Phân quyền | Ổn — nhưng trộn lẫn security techniques và RBAC matrix |
| 11 | Demo (placeholder) | Không cần thiết — nên gộp vào slide Chức năng & Giao diện |
| 12 | Demo Giao diện | Ổn — nhưng tách ra 2 slide làm loãng nội dung |
| 13 | Hạn chế hệ thống | Có "No Soft Delete" — **sai thực tế** (hệ thống đã có RESTRICT FK bảo vệ, không phải lỗi) |
| 14 | Hướng phát triển | Ổn — 3 phase roadmap |
| 15 | Tổng kết | Ổn |
| 16 | Cảm ơn | Ổn |

### File B (Draft-LMS-Slides.pptx — 10 slides)

| Slide | Tiêu đề | Đánh giá |
|---|---|---|
| 1 | Cover | **Vi phạm framing** — subtitle không phù hợp với định vị đồ án Python tự thiết kế |
| 2 | Mục tiêu & Chức năng | Ổn — có actor workflow table |
| 3 | Công nghệ sử dụng | Tốt hơn File A — có đủ HTMX, Tailwind, Alpine.js, Chart.js |
| 4 | Kiến trúc dự án | Tốt — có layer responsibilities, đề cập Separation of Concerns |
| 5 | Môi trường thực nghiệm | Không cần thiết cho bảo vệ — thông tin setup quá chi tiết |
| 6 | ERD & CSDL | Ổn — có 5 entities nhưng thiếu quan hệ và ràng buộc |
| 7 | Quy trình nghiệp vụ | Tốt — 3 luồng rõ ràng trong bảng |
| 8 | Phân quyền RBAC | Tốt — có role definitions và permission matrix |
| 9 | Chức năng & Giao diện | Ổn — 4 module nhưng thiếu screenshots |
| 10 | Tổng kết | **Vi phạm framing** — achievement bullet đầu tiên không phù hợp với định vị đồ án Python tự thiết kế |

---

## 2. Missing Presentation Content

### 2.1 Nội dung thiếu hoàn toàn

| Nội dung thiếu | Tầm quan trọng | Có trong doc nào |
|---|---|---|
| **HTMX live search** — điểm kỹ thuật nổi bật nhất của UI | Cao | DESIGN_DOC.md §10 |
| **Dual Authentication** — Bearer token (API) vs httponly cookie (Web) | Cao | PROJECT_ANALYSIS.md §3 |
| **Tồn kho kép** (quantity vs available_quantity) — cơ chế cốt lõi | Cao | PROJECT_ANALYSIS.md §9 |
| **Category entity** trong ERD — 5 entities không phải 4 | Trung bình | PROJECT_ANALYSIS.md §9 |
| **ON DELETE behavior** trong quan hệ DB (RESTRICT vs CASCADE vs SET NULL) | Trung bình | PROJECT_ANALYSIS.md §9 |
| **Sync Overdue flow** — luồng nghiệp vụ thứ 5 | Trung bình | DESIGN_DOC.md §8 |
| **Dashboard KPI chi tiết** — fine collected/outstanding, top books | Trung bình | PROJECT_ANALYSIS.md §8 |

### 2.2 Nội dung sai hoặc cần chỉnh

| Vấn đề | File | Mô tả |
|---|---|---|
| **"MVC Pattern"** (Slide 6 File A) | File A | Hệ thống không dùng MVC — đây là Layered Architecture 4 tầng (Presentation → Service → Repository → Data). Gọi là MVC sẽ bị hỏi và khó bảo vệ. |
| **"No Soft Delete là hạn chế"** (Slide 13 File A) | File A | Sai — hệ thống đã có RESTRICT FK ngăn xóa sách/user có phiếu mượn ở DB level. Đây là thiết kế có chủ đích. |
| **Framing subtitle không đúng** (Slide 1, 10 File B) | File B | Vi phạm tuyệt đối quy tắc framing — đây là đồ án Python tự thiết kế |
| **Tech stack thiếu** (Slide 4 File A) | File A | HTMX, TailwindCSS, Alpine.js, Chart.js — 4 công nghệ frontend quan trọng bị bỏ qua |
| **"Borrow online" cho Reader** (Slide 10 File B) | File B | Không chính xác — Reader không tự mượn online, phải qua Thủ thư |

### 2.3 Slides thừa hoặc cần gộp

| Slide thừa | Đề xuất |
|---|---|
| **Slide 11 (Demo placeholder)** File A | Xóa — không có nội dung, làm gián đoạn flow |
| **Slide 6 (MVC Pattern) + Slide 7 (Code Structure)** File A | Gộp thành 1 slide "Cấu trúc dự án" với folder tree + layer responsibilities |
| **Slide 9 (API Flow) + Slide 10 (RBAC)** File A | Tách nội dung đúng hơn: Slide 7 = Business Logic Flow, Slide 8 = RBAC |
| **Slide 5 (Setup & Environment)** File B | Xóa — không phù hợp bảo vệ học thuật, chỉ để demo hướng dẫn |

---

## 3. Recommended Slide Improvements

### Slide "Công nghệ sử dụng" (hiện tại Slide 4 File A)

**Vấn đề:** Thiếu 4 công nghệ frontend (HTMX, TailwindCSS, Alpine.js, Chart.js)

**Cải tiến:** Chia theo tầng như File B — Backend / Frontend / Security / Quality. Thêm cột "Lý do chọn" thay vì chỉ liệt kê.

### Slide "Kiến trúc hệ thống" (hiện tại Slide 5 File A)

**Vấn đề:** Không có dual auth, không nhấn Layered Architecture rõ ràng

**Cải tiến:** Sơ đồ 2 luồng: Web UI (cookie) và REST API (bearer token) hội tụ vào FastAPI → Service → Repository → DB. Thêm bảng 4 tầng với trách nhiệm.

### Slide "Cấu trúc dự án" (gộp Slide 6+7 File A)

**Vấn đề:** MVC không chính xác, folder tree và module table tách biệt

**Cải tiến:** Bỏ "MVC", thay bằng "Layered Architecture". Giữ folder tree + bảng module responsibilities trong 1 slide.

### Slide "ERD & CSDL" (Slide 8 File A / Slide 6 File B)

**Vấn đề:** Thiếu Category, thiếu tồn kho kép, thiếu ON DELETE

**Cải tiến:** 5 entities đầy đủ. Thêm hộp giải thích `quantity vs available_quantity`. Thêm bảng ON DELETE behavior.

### Slide "Business Logic Flow" (Slide 9 File A → quá kỹ thuật)

**Vấn đề:** 10 bước internal implementation, liệt kê endpoint — không phù hợp bảo vệ

**Cải tiến:** 3 flowchart nghiệp vụ dạng mũi tên: Mượn → Trả → Gia hạn. Tập trung vào điểm kiểm tra và kết quả, không phải code steps.

### Slide "Hạn chế" (Slide 13 File A)

**Vấn đề:** "No Soft Delete" sai thực tế; thiếu hạn chế quan trọng hơn (sync manual, no email)

**Cải tiến:** Xóa mục "No Soft Delete". Thêm: Sync Overdue thủ công, Không có email notification. Giữ: SQLite concurrency, No rate limiting.

---

## 4. Recommended New Slides

| Slide mới | Lý do | Nội dung |
|---|---|---|
| Không cần thêm slide mới | Target là 10 slides — cần cắt bớt từ 16 (File A) hoặc tái cấu trúc | Xem outline bên dưới |

---

## 5. Recommended Visuals

| Slide | Visual đề xuất |
|---|---|
| Giới thiệu đề tài | Sơ đồ 2 cột: Thủ công (giấy tờ) → Hệ thống số (web) |
| Công nghệ sử dụng | Icon grid theo 4 tầng: Backend / Frontend / Security / Tools |
| Kiến trúc hệ thống | Sơ đồ flow dọc: Browser → FastAPI → Service → Repository → SQLite, với 2 nhánh Auth |
| Cấu trúc dự án | Folder tree ASCII + bảng tầng bên cạnh |
| ERD & CSDL | Sơ đồ hộp-quan hệ 5 entities + callout tồn kho kép |
| Business Logic Flow | 3 flowchart nhỏ ngang: Mượn / Trả / Gia hạn |
| Roles & Phân quyền | Bảng ma trận ✓/— với màu sắc theo vai trò |
| Chức năng & Giao diện | Screenshots thực tế: Dashboard / Book list / Issue form / Reader portal |
| Kết luận & Hướng phát triển | Bảng 2 cột: Đã đạt / Tương lai |

---

## 6. Final Presentation Outline — 10 Slides

---

### SLIDE 1 — Giới thiệu đề tài

**Mục tiêu:** Hook bằng bài toán thực tế → giới thiệu giải pháp

**Key bullets:**
- Thư viện truyền thống: sổ sách giấy → khó kiểm soát tồn kho, không có báo cáo tức thời
- Giải pháp: Hệ thống quản lý thư viện trực tuyến full-stack bằng Python
- Đối tượng: Độc giả · Thủ thư · Quản trị viên
- Phạm vi: Quản lý kho sách · Lưu thông sách · Phân quyền 3 cấp · Dashboard thống kê

**Visual đề xuất:** Sơ đồ chuyển đổi: [Giấy tờ thủ công] → [Hệ thống web Python]. Icons đơn giản cho 3 vai trò.

**Speaker notes:**
> Mở đầu: "Thư viện truyền thống quản lý bằng sổ tay — không kiểm soát được tồn kho real-time, không có báo cáo tức thời, không theo dõi được sách quá hạn. Đề tài này xây dựng hệ thống web Python giải quyết toàn bộ bài toán đó, với giao diện web và REST API trong cùng một ứng dụng."

---

### SLIDE 2 — Mục tiêu hệ thống

**Mục tiêu:** Trình bày 5 mục tiêu cụ thể, đo lường được

**Key bullets:**
- Số hoá lưu thông sách — tạo/theo dõi phiếu mượn, cập nhật tồn kho tức thời
- Tự động tính phí phạt — số ngày quá hạn × 5.000 VND, không cần tính tay
- Kiểm soát tồn kho real-time — `available_quantity` cập nhật ngay khi cấp phát / trả
- Thống kê hoạt động — Dashboard KPI + biểu đồ + top sách/reader
- Cung cấp REST API đầy đủ — Swagger UI tự động, có thể tích hợp ngoài

**Visual đề xuất:** Bảng 5 hàng với icon mô tả mục tiêu, cột "Kết quả cụ thể".

**Speaker notes:**
> "Hệ thống hướng đến 5 mục tiêu rõ ràng. Quan trọng nhất là: tự động hóa hoàn toàn việc tính phí phạt và kiểm soát tồn kho real-time — hai điểm mà quản lý thủ công hay sai nhất."

---

### SLIDE 3 — Công nghệ sử dụng

**Mục tiêu:** Giới thiệu tech stack theo tầng, giải thích lý do chọn

**Key bullets:**
- **Backend:** Python 3.12 · FastAPI (async, auto-docs) · Uvicorn (ASGI server)
- **Database:** SQLite · SQLAlchemy 2.x async ORM · Alembic (migration)
- **Frontend:** Jinja2 SSR · HTMX (live search, không reload) · Alpine.js · TailwindCSS · Chart.js
- **Security:** PyJWT · bcrypt · Pydantic v2

**Visual đề xuất:** Grid 4 tầng (hộp màu): Backend / Frontend / Security / Quality. Mỗi tầng liệt kê logo/tên công nghệ.

**Speaker notes:**
> "Điểm khác biệt của stack này: HTMX cho phép live search và cập nhật bảng không cần reload trang, mà không cần viết JavaScript SPA. FastAPI tự sinh Swagger UI từ Pydantic schema — không cần viết tài liệu API thủ công."

---

### SLIDE 4 — Tổng quan kiến trúc hệ thống

**Mục tiêu:** Trình bày kiến trúc Monolith Full-stack và Pattern 4 tầng

**Key bullets:**
- Kiến trúc Monolith Full-stack — 1 server FastAPI phục vụ cả Web UI và REST API
- Pattern 4 tầng: Presentation → Service → Repository → Data
- Dual Authentication: Bearer Token (REST API) · httponly Cookie (Web UI)
- RBAC 3 cấp: Reader ⊂ Librarian ⊂ Admin — enforce ở Dependency layer

**Visual đề xuất:**
```
[Browser]
    |-- Web UI (Jinja2+HTMX) --> Cookie Auth
    |-- REST API (JSON)      --> Bearer Token
              |
         [FastAPI App]
              |
    [Service Layer] -- Business Rules
              |
    [Repository Layer] -- Async DB Queries
              |
         [SQLite DB]
```

**Speaker notes:**
> "Một server FastAPI duy nhất phục vụ hai giao diện. Web UI dùng cookie để bảo mật hơn cho browser — JavaScript không đọc được httponly cookie. REST API dùng Bearer token cho client code. Cả hai hội tụ vào cùng Service layer."

---

### SLIDE 5 — Cấu trúc dự án

**Mục tiêu:** Cho thấy tổ chức module rõ ràng theo Layered Architecture

**Key bullets:**
- `models/` — 5 ORM entities: User · Book · Category · Borrowing · Review
- `repositories/` — Data access layer: async queries, không có business logic
- `services/` — Business logic: kiểm tra quy tắc nghiệp vụ trước DB
- `api/v1/` + `web/` — REST API (JSON) và Web UI (SSR Jinja2)
- `dependencies/` — JWT auth + RBAC injection

**Visual đề xuất:** Folder tree cô đọng bên trái + bảng tầng và trách nhiệm bên phải.

**Speaker notes:**
> "Nguyên tắc thiết kế: mỗi tầng chỉ làm đúng một việc. Service layer giữ toàn bộ business rule — không có logic trong router, không có logic trong repository. Điều này giúp dễ test và dễ thay đổi từng phần."

---

### SLIDE 6 — ERD & Thiết kế cơ sở dữ liệu

**Mục tiêu:** Trình bày 5 entities, quan hệ, và 2 cơ chế thiết kế quan trọng

**Key bullets:**
- 5 entities: users · books · categories · borrowings · reviews
- Tồn kho kép: `quantity` (tổng) vs `available_quantity` (hiện có) — cập nhật ngay khi mượn/trả
- Phí phạt: `fine_amount = days_overdue × 5.000 VND` · `fine_paid` theo dõi thu tiền
- ON DELETE: RESTRICT (borrowings) · CASCADE (reviews) · SET NULL (category → books)
- Unique constraint: `(user_id, book_id)` trong reviews — 1 review/sách/user

**Visual đề xuất:** Sơ đồ ERD 5 hộp với đường quan hệ + callout box "Tồn kho kép" và "Fine logic".

**Speaker notes:**
> "Hai điểm thiết kế đáng chú ý: Tồn kho kép cho phép biết ngay bao nhiêu bản đang có sẵn mà không cần đếm phiếu mượn. RESTRICT FK ngăn xóa sách hay user còn phiếu mượn — bảo vệ tính toàn vẹn dữ liệu ở tầng DB."

---

### SLIDE 7 — Business Logic Flow

**Mục tiêu:** Trình bày 3 luồng nghiệp vụ cốt lõi dạng flowchart

**Key bullets:**
- **Mượn:** Thủ thư live-search → Kiểm tra 5 điều kiện → Tạo phiếu → `available_quantity -= 1`
- **Trả:** Chọn phiếu → Ghi tình trạng → Tính phạt tự động → `available_quantity += 1` → Thu phạt
- **Gia hạn:** Kiểm tra `renewed_count < 2` → `due_date += 14 ngày`
- Quy tắc cứng: max 5 phiếu active/reader · max 2 gia hạn · 5.000 VND/ngày
- Sync Overdue: Admin kích hoạt → cập nhật hàng loạt status + fine_amount

**Visual đề xuất:** 3 flowchart nhỏ nằm ngang, mỗi luồng 4–5 bước với điểm kiểm tra màu đỏ (FAIL) và xanh (PASS).

**Speaker notes:**
> "3 điểm kiểm tra quan trọng trong luồng mượn: sách phải có sẵn, reader chưa đủ 5 phiếu active, và reader chưa đang mượn cuốn đó. Tất cả đều do Service layer kiểm tra trước khi chạm vào DB."

---

### SLIDE 8 — Roles & Phân quyền

**Mục tiêu:** Trình bày hệ thống RBAC 3 cấp và cơ chế bảo mật

**Key bullets:**
- 3 vai trò theo thứ bậc: Reader ⊂ Librarian ⊂ Admin
- Phân quyền theo nhóm chức năng: Public · Tự phục vụ · Lưu thông · Quản lý · Dashboard
- Enforce 2 lớp: FastAPI Dependency (API) và Web route dependency (Cookie)
- Reader isolation: chỉ thấy phiếu của bản thân — kiểm tra ở service + query
- Bảo mật: bcrypt hash · JWT access 60' + refresh 7 ngày · httponly cookie · CORSMiddleware

**Visual đề xuất:** Bảng ma trận phân quyền với màu: xanh lá (✓), xám (—), phân biệt màu nền theo vai trò.

**Speaker notes:**
> "RBAC được enforce ở 2 lớp độc lập: Dependency Injection cho REST API và Web route middleware cho Web UI. Reader không thể xem phiếu của người khác dù biết ID — kiểm tra được thực hiện ở cả service layer lẫn DB query."

---

### SLIDE 9 — Chức năng hệ thống & Giao diện

**Mục tiêu:** Demo 4 module chính qua screenshots thực tế

**Key bullets:**
- **Kho sách:** Tìm kiếm live (HTMX), lọc thể loại/ngôn ngữ, upload ảnh bìa
- **Lưu thông:** Live search cấp phát, tự động tính phạt, quản lý phiếu mượn
- **Tự phục vụ:** Reader xem phiếu, gia hạn, lịch sử, đánh giá sách
- **Dashboard:** KPI cards · Biểu đồ mượn/trả Chart.js · Top 5 sách/reader · Bảng tồn kho

**Visual đề xuất:** Grid 2×2 screenshots giao diện thực tế: Admin Dashboard / Book List / Issue Form / Reader Portal. Highlight HTMX live search bằng annotation mũi tên.

**Speaker notes:**
> "Điểm nổi bật nhất về UX: live search dùng HTMX — gõ tên sách là bảng kết quả cập nhật ngay, không reload trang, không viết một dòng JavaScript. Dashboard lấy dữ liệu từ SQL aggregation query và render Chart.js — không có data fake."

---

### SLIDE 10 — Kết luận, Hạn chế & Hướng phát triển

**Mục tiêu:** Tổng kết kết quả, thừa nhận hạn chế tự tin, định hướng tương lai

**Key bullets:**
- **Đã đạt:** REST API + Web UI dual interface · Layered Architecture · RBAC 3 cấp · Phí phạt tự động tại thời điểm trả sách · Swagger UI
- **Hạn chế thực tế:** SQLite (single-writer) · Sync Overdue thủ công · Không có email notification · Không có export báo cáo
- **Cải tiến gần:** Thêm APScheduler cho auto sync · Rate limiting (slowapi) · Async file upload
- **Tương lai:** PostgreSQL · Email notification · Docker + CI/CD · Export PDF/Excel · Book reservation

**Visual đề xuất:** 2 cột song song: Đã đạt (checkmark xanh) vs Hướng phát triển (mũi tên). Timeline roadmap nhỏ phía dưới.

**Speaker notes:**
> "Hệ thống đáp ứng đầy đủ yêu cầu đề tài: phân quyền rõ ràng, nghiệp vụ chính xác, kiến trúc có thể mở rộng. Hạn chế lớn nhất là SQLite không phù hợp production quy mô lớn và chưa có thông báo tự động — cả hai đều có lộ trình cụ thể để giải quyết."

---

## 7. Slide Restructuring Summary

### Từ File A (16 slides) → 10 slides theo cấu trúc đề xuất

| Slide cũ (File A) | Xử lý | Slide mới |
|---|---|---|
| Slide 1 (Cover) | Giữ nguyên | Cover (nằm ngoài 10 slides nội dung) |
| Slide 2 (Giới thiệu) | Giữ, tinh chỉnh | → Slide 1: Giới thiệu đề tài |
| — | Tạo mới từ DESIGN_DOC | → Slide 2: Mục tiêu hệ thống |
| Slide 4 (Tech Stack) | Bổ sung HTMX/Tailwind/Alpine/Chart | → Slide 3: Công nghệ sử dụng |
| Slide 5 (Architecture) | Thêm dual auth, làm rõ 4 tầng | → Slide 4: Kiến trúc hệ thống |
| Slide 6 (MVC) + Slide 7 (Structure) | Gộp, đổi tên, bỏ "MVC" | → Slide 5: Cấu trúc dự án |
| Slide 8 (ERD) | Bổ sung Category, tồn kho kép, ON DELETE | → Slide 6: ERD & Thiết kế CSDL |
| Slide 9 (API Flow) | Chuyển sang nghiệp vụ, bỏ technical steps | → Slide 7: Business Logic Flow |
| Slide 10 (Security+RBAC) | Tách: RBAC riêng + security tóm gọn | → Slide 8: Roles & Phân quyền |
| Slide 11 (Demo) + Slide 12 (UI) | Gộp, thêm screenshots thực tế | → Slide 9: Chức năng & Giao diện |
| Slide 13+14+15 (Hạn chế+Roadmap+Summary) | Gộp, sửa nội dung sai | → Slide 10: Kết luận, Hạn chế & Hướng phát triển |
| Slide 3 (Core Features) | Phân tán vào Slide 1, 2, 9 | Loại bỏ |
| Slide 16 (Cảm ơn) | Giữ | Cover cuối (nằm ngoài 10 slides nội dung) |

### Nội dung cần xóa khỏi slides

| Vị trí | Nội dung cần xóa | Lý do |
|---|---|---|
| File B Slide 1 | Subtitle không phù hợp với định vị đồ án Python tự thiết kế | Vi phạm tuyệt đối quy tắc framing đồ án |
| File B Slide 10 | Achievement bullet đầu không phù hợp với định vị đồ án Python tự thiết kế | Vi phạm tuyệt đối quy tắc framing đồ án |
| File A Slide 6 | Toàn bộ khung MVC | Không đúng với kiến trúc thực tế của hệ thống |
| File A Slide 13 | Mục "No Soft Delete" trong hạn chế | Sai thực tế — hệ thống đã có RESTRICT FK bảo vệ |
| File A Slide 9 | 10 bước internal implementation | Quá kỹ thuật, không phù hợp bảo vệ |
