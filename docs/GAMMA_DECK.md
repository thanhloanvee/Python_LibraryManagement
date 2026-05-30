# GAMMA_DECK.md — Hệ Thống Quản Lý Thư Viện
## Phase 3 Part C · Gamma-Compatible Presentation Deck

> **Theme:** Pastel blue palette · Montserrat font · Modern academic · 10 slides · 16:9
> **Audience:** Hội đồng bảo vệ đồ án · Kỹ thuật lập trình Python
> **Ngôn ngữ:** Tiếng Việt (nội dung chính) · English (thuật ngữ kỹ thuật)

---

## Slide 1 — Giới thiệu đề tài

**Hệ Thống Quản Lý Thư Viện Trực Tuyến**

* Thư viện truyền thống: sổ sách giấy → khó kiểm soát tồn kho, không có báo cáo tức thời
* Giải pháp: ứng dụng web full-stack bằng **Python / FastAPI**
* 3 vai trò người dùng: **Độc giả · Thủ thư · Quản trị viên**
* Phạm vi: quản lý kho sách · lưu thông mượn/trả · phân quyền · thống kê

Visual Suggestion:
Sơ đồ 2 cột đối xứng — trái: icon tập hồ sơ giấy (thủ công) · phải: icon màn hình web (hệ thống số).
Mũi tên lớn chỉ từ trái sang phải. Ba icon nhỏ phía dưới: người đọc sách · nhân viên · quản trị viên.
Màu nền: pastel blue nhạt. Tiêu đề Montserrat Bold 40px.

---

## Slide 2 — Mục tiêu hệ thống

**Mục Tiêu Hệ Thống**

* Số hoá lưu thông sách — phiếu mượn & tồn kho cập nhật **real-time**
* Tính phí phạt tại thời điểm trả sách — `ngày quá hạn × 5.000 VND`, không cần tính tay
* Cung cấp **REST API** đầy đủ kèm Swagger UI tự động
* Dashboard thống kê — KPI · biểu đồ theo tháng · top sách/reader
* Phân quyền 3 cấp rõ ràng — **Reader ⊂ Librarian ⊂ Admin**

Visual Suggestion:
5 hàng, mỗi hàng gồm: icon nhỏ bên trái + tên mục tiêu bold + mô tả kết quả bên phải.
Icon gợi ý: cuốn sách · đồng hồ · API brackets · biểu đồ cột · khóa bảo mật.
Nền trắng, viền card pastel blue, font Montserrat Regular 20px.

---

## Slide 3 — Công nghệ sử dụng

**Tech Stack — Theo Tầng**

* **Backend:** Python 3.12 · FastAPI (async, auto-docs) · Uvicorn · SQLAlchemy 2.x · SQLite · Alembic
* **Frontend:** Jinja2 SSR · HTMX (live search, không reload) · Alpine.js · TailwindCSS · Chart.js
* **Security:** PyJWT · bcrypt · Pydantic v2 · itsdangerous
* **Quality:** pytest · pytest-asyncio · httpx · Ruff

Visual Suggestion:
Grid 4 ô theo tầng, mỗi ô có màu nền pastel khác nhau (xanh dương / xanh lá nhạt / tím nhạt / cam nhạt).
Trong mỗi ô: tên tầng Montserrat Bold + danh sách badge tên công nghệ dạng pill/chip.
Không cần logo — text pill đủ rõ ràng cho slide bảo vệ.

---

## Slide 4 — Tổng quan kiến trúc hệ thống

**Kiến Trúc Monolith Full-Stack**

* 1 server **FastAPI** phục vụ cả Web UI (SSR) và REST API (JSON)
* **Layered Architecture** 4 tầng: Presentation → Service → Repository → Data
* **Dual Auth:** httponly Cookie (Web UI) · Bearer Token (REST API)
* RBAC enforce tại **Dependency layer** — toàn bộ endpoint hiện tại đều được kiểm soát tập trung

Visual Suggestion:
Sơ đồ dọc, từ trên xuống:
[Trình duyệt] → 2 nhánh: [Web UI / Cookie] và [REST API / Bearer Token]
Hội tụ vào [FastAPI App] → [Service Layer] → [Repository Layer] → [SQLite DB].
Mỗi hộp màu pastel blue đậm dần từ trên xuống. Mũi tên có nhãn.
Cạnh phải: bảng nhỏ 4 hàng liệt kê tầng + trách nhiệm.

---

## Slide 5 — Cấu trúc dự án

**Layered Architecture — Tổ Chức Module**

* `models/` — 5 ORM entities: User · Book · Category · Borrowing · Review
* `repositories/` — async DB queries, **không có** business logic
* `services/` — toàn bộ business rules, kiểm tra trước khi chạm DB
* `api/v1/` + `web/` — REST endpoints (JSON) và Web UI (Jinja2 SSR)
* `dependencies/` — JWT verification · RBAC role injection

Visual Suggestion:
Bố cục 2 cột: trái là folder tree dạng monospace (cô đọng 8–10 dòng), phải là bảng 5 hàng module + trách nhiệm.
Highlight `services/` bằng viền màu vàng nhạt — nhấn đây là tầng quan trọng nhất.
Font monospace cho folder tree, Montserrat cho bảng.

---

## Slide 6 — ERD & Thiết kế cơ sở dữ liệu

**5 Entities · Quan Hệ · Ràng Buộc**

* **5 bảng:** users · books · categories · borrowings · reviews
* **Tồn kho kép:** `quantity` (tổng bản) vs `available_quantity` (có sẵn) — tự động cập nhật
* **Phí phạt:** `fine_amount = days_overdue × 5.000 VND` · `fine_paid` theo dõi thu tiền
* **ON DELETE:** RESTRICT (borrowings) · CASCADE (reviews) · SET NULL (categories)
* **Unique:** `(user_id, book_id)` trong reviews — 1 review / sách / reader

Visual Suggestion:
ERD diagram 5 hộp chữ nhật bo góc, bố trí theo hình chữ thập:
- Trung tâm: borrowings · Trên: users · Phải: books · Góc trên phải: reviews · Góc trên trái: categories.
Đường kẻ quan hệ có nhãn ON DELETE. Callout box nhỏ bên cạnh books: "quantity = 5 / available = 3".

---

## Slide 7 — Business Logic Flow

**3 Luồng Nghiệp Vụ Cốt Lõi**

* **Mượn:** Live-search reader + sách → 5 kiểm tra → tạo phiếu → `available_quantity -= 1`
* **Trả:** Ghi tình trạng sách → tính phạt tự động → `available_quantity += 1` → xác nhận thu tiền
* **Gia hạn:** Kiểm tra `renewed_count < 2` → `due_date += 14 ngày`
* Quy tắc cứng: tối đa **5 phiếu active** / reader · tối đa **2 lần gia hạn**
* Sync Overdue: Admin kích hoạt → cập nhật hàng loạt trạng thái + fine_amount

Visual Suggestion:
3 flowchart nhỏ nằm ngang, mỗi cái 4–5 bước hình thoi + hình chữ nhật:
[Mượn] [Trả] [Gia hạn] — cạnh nhau theo chiều ngang.
Hình thoi (điều kiện) màu đỏ nhạt khi FAIL, xanh lá nhạt khi PASS.
Phía dưới: thanh horizontal bar "Business Rules" với 2 badge số: 5 phiếu · 2 gia hạn · 5.000 VND/ngày.

---

## Slide 8 — Roles & Phân quyền

**RBAC — Reader ⊂ Librarian ⊂ Admin**

* **Reader:** Duyệt sách · xem phiếu cá nhân · gia hạn · đánh giá sách
* **Librarian:** Reader + cấp phát sách · xử lý trả · thu phí phạt
* **Admin:** Librarian + quản lý kho · quản lý user · dashboard thống kê
* Enforce **2 lớp:** FastAPI Dependency (API) · Web route middleware (Cookie)
* Reader **chỉ thấy dữ liệu của bản thân** — isolation kiểm tra tại service + query

Visual Suggestion:
Bảng ma trận phân quyền: hàng = nhóm chức năng (5 nhóm), cột = 3 vai trò.
Ô ✓ màu xanh lá nhạt, ô — màu xám nhạt.
Tiêu đề cột có badge màu phân biệt: Reader (xanh dương) · Librarian (xanh lá) · Admin (tím).
Phía dưới bảng: 2 badge nhỏ "API: Bearer Token" và "Web: httponly Cookie".

---

## Slide 9 — Chức năng hệ thống & Giao diện

**4 Module Chính**

* **Kho sách:** Tìm kiếm live (HTMX), lọc đa điều kiện, upload ảnh bìa
* **Lưu thông:** Live-search cấp phát, tính phạt tự động, quản lý phiếu mượn
* **Tự phục vụ:** Reader xem phiếu · gia hạn · lịch sử · đánh giá sách
* **Dashboard Admin:** KPI cards · Chart.js biểu đồ theo tháng · Top 5 sách/reader

Visual Suggestion:
Grid 2×2 screenshots giao diện thực tế của ứng dụng:
- Ô trên trái: Admin Dashboard với KPI cards và biểu đồ cột Chart.js
- Ô trên phải: Trang danh sách sách với live search HTMX (annotation mũi tên: "Live search — không reload")
- Ô dưới trái: Form cấp phát sách (Issue Book) với live search reader
- Ô dưới phải: Reader portal — danh sách phiếu mượn và nút gia hạn
Viền bo góc pastel blue, caption nhỏ dưới mỗi ô.

---

## Slide 10 — Kết luận, Hạn chế & Hướng phát triển

**Tổng Kết Đề Tài**

* **Đạt được:** REST API + Web UI dual · Layered Architecture · RBAC 3 cấp · phí phạt tự động tại thời điểm trả sách · Swagger UI
* **Hạn chế:** SQLite (single-writer) · Sync Overdue thủ công · chưa có email notification · chưa có export báo cáo
* **Cải tiến gần:** APScheduler (auto sync) · rate limiting · async file upload
* **Tương lai:** PostgreSQL · email notification · Docker + CI/CD · export PDF/Excel

Visual Suggestion:
Bố cục 2 cột song song:
- Cột trái "Đã đạt được" — danh sách bullet với checkmark icon màu xanh lá
- Cột phải "Hướng phát triển" — danh sách bullet với mũi tên icon màu xanh dương
Phía dưới: timeline ngang 2 giai đoạn "Cải tiến gần" và "Tương lai" với badge pill.
Nền slide: gradient pastel blue rất nhạt. Font Montserrat Medium 20px.
