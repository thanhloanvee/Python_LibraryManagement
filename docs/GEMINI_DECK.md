# GEMINI_DECK.md — Hệ thống Quản lý Thư viện
## Gemini-Compatible Markdown Deck · 10 Slides

> **Theme:** Pastel blue · Montserrat · Modern academic · 16:9
> **Language:** Tiếng Việt + English terms
> **Audience:** University defense panel

---

## Slide 1 — Giới thiệu đề tài

* Thư viện truyền thống: ghi sổ tay → sai sót, mất thông tin, không có báo cáo
* Giải pháp: **Số hoá toàn bộ** quy trình mượn · trả · gia hạn · phạt · thống kê
* Nâng cấp từ hệ thống cũ (PHP) lên nền tảng Python hiện đại
* Một hệ thống — hai đầu ra: **Giao diện Web** cho nhân viên + **REST API** cho tích hợp
* Nhóm: Lê Thị Thanh Loan (24210228) · Trần Hưng Khoa (24210220)

**Visual Suggestion:**
Split-screen Before / After — trái: ảnh sổ ghi tay · phải: screenshot trang chủ Web App. Nền pastel blue nhạt, font Montserrat Bold cho tiêu đề.

---

## Slide 2 — Mục tiêu hệ thống

* Số hoá phiếu mượn / trả — thay thế hoàn toàn sổ giấy
* Tồn kho cập nhật **tức thì** khi mượn hoặc trả sách
* Tự động tính phí phạt: số ngày trễ × 5.000 VND
* Phân quyền **3 cấp** rõ ràng: Độc giả · Thủ thư · Quản trị viên
* Dashboard thống kê + REST API sẵn sàng tích hợp mở rộng

**Visual Suggestion:**
Bảng 2 cột màu pastel: *Mục tiêu* | *Giải pháp trong hệ thống* — icon check xanh lá mỗi dòng. Viền bo tròn, nền trắng.

---

## Slide 3 — Công nghệ sử dụng

* **Backend:** Python 3.12 · FastAPI · Uvicorn — hiệu năng cao, tự sinh tài liệu API
* **Database:** SQLite · SQLAlchemy ORM · Alembic — quản lý schema có kiểm soát
* **Frontend:** Jinja2 SSR · HTMX · Alpine.js · TailwindCSS · Chart.js
* **Bảo mật:** JWT Token · Bcrypt · Pydantic v2 validation
* **Kiểm thử:** pytest · httpx — 18 test cases (auth · sách · phiếu mượn)

**Visual Suggestion:**
Layer diagram 4 tầng dọc — mỗi tầng một màu pastel khác nhau (xanh dương · xanh lá · cam nhạt · tím nhạt). Tên công nghệ kèm logo nhỏ. Mũi tên luồng từ trên xuống.

---

## Slide 4 — Kiến trúc hệ thống

* Kiến trúc **Monolith Full-stack** — 1 server FastAPI, 2 giao diện độc lập
* **Web UI** (`/`, `/admin/*`, `/reader/*`) — đăng nhập bằng Cookie bảo mật
* **REST API** (`/api/v1/*`) — đăng nhập bằng JWT Token · Swagger UI tại `/api/docs`
* Phân tầng: Giao diện → Nghiệp vụ → Truy vấn dữ liệu → Cơ sở dữ liệu
* Toàn bộ quy tắc nghiệp vụ tập trung tại **Service layer** — không rải rác

**Visual Suggestion:**
Diagram dọc 2 nhánh: nhánh trái "Web UI / Cookie" · nhánh phải "REST API / JWT" — hội tụ tại khối "Service Layer" ở giữa, sau đó xuống "Database". Màu pastel, nhãn tiếng Việt.

---

## Slide 5 — Cấu trúc dự án

* **models/** — 5 thực thể: Người dùng · Sách · Thể loại · Phiếu mượn · Đánh giá
* **services/** — Toàn bộ nghiệp vụ: Xác thực · Mượn/Trả · Sách · Thống kê
* **repositories/** — Truy vấn dữ liệu thuần tuý, không chứa nghiệp vụ
* **api/v1/** + **web/** — REST endpoints (JSON) · Web UI endpoints (HTML)
* **dependencies/** — Xác thực danh tính + Kiểm soát phân quyền tập trung

**Visual Suggestion:**
Card diagram 4 tầng màu pastel — xanh = giao diện (api · web) · vàng = nghiệp vụ (services) · cam = dữ liệu (repositories) · tím = mô hình (models · schemas). Tên thư mục thực tế bên trong mỗi card.

---

## Slide 6 — Thiết kế cơ sở dữ liệu

* 5 bảng: **Người dùng · Thể loại · Sách · Phiếu mượn · Đánh giá**
* Phiếu mượn lưu: ngày mượn · hạn trả · tiền phạt · số lần gia hạn · tình trạng sách
* Sách tách biệt *tổng số bản* và *số bản còn sẵn* để theo dõi real-time
* Ràng buộc **bảo vệ dữ liệu**: không xoá sách / người dùng khi còn phiếu chưa trả
* Mỗi độc giả chỉ được đánh giá **một lần** mỗi cuốn sách

**Visual Suggestion:**
ERD diagram 5 bảng — đường quan hệ tô màu theo chiến lược: đỏ nhạt = chặn xoá · xanh = xoá theo · xám = giữ nguyên. Cardinality 1–N rõ ràng, font Montserrat, nền trắng viền xanh.

---

## Slide 7 — Quy trình nghiệp vụ

**Mượn sách:**
* Thủ thư tìm độc giả + sách → hệ thống kiểm tra 4 điều kiện tự động
* Đạt tất cả → phiếu mượn được tạo · hạn trả = hôm nay + 14 ngày · tồn kho giảm 1

**Trả sách:**
* Ghi nhận tình trạng sách → hệ thống tự tính phạt → tồn kho tăng 1 → xác nhận thu tiền

**Gia hạn:**
* Tối đa 2 lần · hạn trả tự động cộng thêm 14 ngày mỗi lần

**Đồng bộ quá hạn:**
* Quản trị viên kích hoạt → hệ thống quét và cập nhật toàn bộ phiếu quá ngày trả

**Visual Suggestion:**
Flowchart dọc quy trình Mượn sách — 4 hình thoi điều kiện (đỏ nhạt = không đạt / xanh = đạt) · mini-flowchart Trả sách đặt bên phải. Bảng nhỏ "Quy tắc nghiệp vụ" ở góc dưới.

---

## Slide 8 — Phân quyền hệ thống

* **Chưa đăng nhập:** Duyệt sách · Xem chi tiết · Đăng ký tài khoản
* **Độc giả:** Xem phiếu của mình · Tự gia hạn · Viết đánh giá sau khi đã mượn
* **Thủ thư:** Cấp phát · Xử lý trả · Xem toàn bộ phiếu · Xác nhận thu phạt
* **Quản trị viên:** Toàn quyền + Quản lý sách · Người dùng · Dashboard · Đồng bộ quá hạn
* Tài khoản bị khoá không thể đăng nhập · Không xoá được khi còn phiếu mượn

**Visual Suggestion:**
Ma trận quyền dạng bảng 5 cột — ô xanh pastel đậm = có quyền · ô đỏ nhạt = không có quyền. Header mỗi cột có icon vai trò nhỏ. Màu nền xen kẽ nhẹ từng dòng.

---

## Slide 9 — Chức năng & Giao diện

* **Trang chủ (Public):** Thống kê nhanh · Danh sách sách · Tìm kiếm · Chi tiết + đánh giá
* **Thủ thư:** Form cấp phát với tìm kiếm trực tiếp (gõ là hiện ngay, không reload trang)
* **Quản trị:** Dashboard KPI · Biểu đồ mượn/trả theo tháng · Top sách & độc giả tích cực
* **Độc giả:** Sách đang mượn · Hạn trả · Nút gia hạn · Lịch sử · Hồ sơ cá nhân
* **REST API:** Tài liệu Swagger UI tự động — sẵn sàng cho mobile / tích hợp bên ngoài

**Visual Suggestion:**
Screenshot grid 2×3: (1) Admin Dashboard + Chart.js · (2) Form cấp phát live search · (3) Danh sách sách tìm kiếm · (4) Chi tiết sách + đánh giá · (5) Form trả sách + tiền phạt · (6) Swagger UI. Bo góc nhẹ, shadow nhạt.

---

## Slide 10 — Kết luận & Hướng phát triển

* **Đã hoàn thành:** Web App + REST API · RBAC 3 cấp · Quy trình lưu thông đầy đủ · Dashboard · 18 test cases
* **Hạn chế thực tế:** Cơ sở dữ liệu phù hợp quy mô nhỏ · Đồng bộ quá hạn thủ công · Chưa có thông báo email
* **Ngắn hạn:** Nâng cấp database production · Tự động đồng bộ theo lịch · Giới hạn tần suất API
* **Trung hạn:** Hệ thống đặt giữ sách · Độc giả tự đặt yêu cầu mượn · Thông báo email
* **Dài hạn:** Ứng dụng di động (tận dụng API có sẵn) · Tích hợp thanh toán · Gợi ý sách thông minh

**Visual Suggestion:**
2 phần ngang: trái — checklist "Đã hoàn thành" (5 dòng, icon check xanh lá) · phải — Timeline roadmap 3 cột Ngắn / Trung / Dài hạn với gradient từ xanh nhạt đến xanh đậm. Dưới cùng: tagline nhỏ *"REST API sẵn sàng — mobile app chỉ cần kết nối, không cần viết lại backend."*

---

## Gemini Deck — Theme Configuration

```
Color palette:
  Primary    #93C5FD   pastel blue (bullets, accents)
  Light      #BFDBFE   light blue (section backgrounds)
  Deep       #1D4ED8   deep blue (headings, borders)
  Background #F0F9FF   ultra-light blue tint
  Text       #1E293B   dark slate
  OK         #86EFAC   pastel green (checkmarks)
  Fail       #FCA5A5   pastel red (restrictions)

Typography:
  All text   Montserrat
  Headings   Bold, Large
  Body       Regular, Medium

Layout:
  Format     16:9 Widescreen
  Style      Clean, Minimal
  Icons      Outlined, minimal (no fill)
  Diagrams   Flat arrows, pastel fills, no drop shadows
  Images     Screenshots with 8px rounded corners, 1px blue border
```

---

## Story Flow

```
Slide 1  —  TẠI SAO    Bài toán → lý do xây dựng hệ thống
Slide 2  —  CÁI GÌ     6 mục tiêu cụ thể đã hiện thực hoá
Slide 3  —  CÔNG CỤ    Công nghệ → vai trò từng thành phần
Slide 4  —  KIẾN TRÚC  1 server · 2 giao diện · 4 tầng xử lý
Slide 5  —  TỔ CHỨC    Cấu trúc dự án → phân tách trách nhiệm
Slide 6  —  DỮ LIỆU    5 bảng · quan hệ · chiến lược bảo vệ
Slide 7  —  NGHIỆP VỤ  4 quy trình: Mượn · Trả · Gia hạn · Đồng bộ
Slide 8  —  PHÂN QUYỀN 4 cấp độ · ma trận quyền · quy tắc đặc biệt
Slide 9  —  DEMO       5 nhóm chức năng · giao diện thực tế
Slide 10 —  KẾT LUẬN   Thành quả · Hạn chế trung thực · Roadmap
```
