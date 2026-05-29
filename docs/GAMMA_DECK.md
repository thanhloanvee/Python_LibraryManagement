# GAMMA_DECK.md — Hệ thống Quản lý Thư viện
## Phase 3 Part C · Gamma-Compatible Presentation Deck

> **Theme:** Pastel blue palette · Montserrat font · Modern academic · 10 slides · 16:9
> **Ngôn ngữ:** Tiếng Việt (nội dung chính) + English (thuật ngữ kỹ thuật)
> **Đối tượng:** Giảng viên thạc sĩ / Hội đồng bảo vệ đồ án

---

## Slide 1 — Giới thiệu đề tài

### Hệ thống Quản lý Thư viện
#### *Library Management System*

**Bài toán thực tế:**
- Thư viện truyền thống ghi sổ tay → dễ sai sót, không kiểm soát được tồn kho
- Không biết sách nào đang mượn, ai đang giữ, sách nào quá hạn
- Không có báo cáo tổng hợp — ban quản lý mù thông tin

**Giải pháp:**
- Số hoá toàn bộ quy trình: mượn · trả · gia hạn · tính phạt · báo cáo
- Xây dựng lại hoàn toàn từ hệ thống cũ sang nền tảng hiện đại hơn
- Phục vụ đồng thời: giao diện Web cho nhân viên & API mở cho tích hợp sau này

**Nhóm thực hiện:**
- Lê Thị Thanh Loan — MSSV 24210228
- Trần Hưng Khoa — MSSV 24210220

**Visual Suggestion:**
```
┌─────────────────────────┬─────────────────────────┐
│         TRƯỚC           │           SAU            │
│   [Hình sổ ghi tay]     │   [Screenshot Web App]  │
│                         │                         │
│  • Ghi sổ thủ công      │  • Theo dõi real-time   │
│  • Dễ mất / sai thông   │  • Tính phạt tự động    │
│    tin                  │  • Báo cáo tức thì      │
│  • Không có báo cáo     │  • Tra cứu dễ dàng      │
└─────────────────────────┴─────────────────────────┘
```
*Split-screen Before / After — tone pastel blue bên phải*

---

## Slide 2 — Mục tiêu hệ thống

### 6 Mục tiêu Cốt lõi

| # | Mục tiêu | Hệ thống giải quyết như thế nào |
|---|---|---|
| 1 | Số hoá phiếu mượn / trả | Quản lý toàn bộ vòng đời phiếu: Đang mượn → Quá hạn → Đã trả |
| 2 | Kiểm soát tồn kho real-time | Số lượng sách có sẵn cập nhật ngay lập tức khi mượn hoặc trả |
| 3 | Tự động tính phí phạt | Hệ thống tự tính: số ngày trễ × 5.000 VND khi xử lý trả sách |
| 4 | Phân quyền 3 cấp rõ ràng | Độc giả · Thủ thư · Quản trị viên — mỗi cấp thấy đúng chức năng của mình |
| 5 | Dashboard thống kê | Tổng quan KPI · Biểu đồ hoạt động · Danh sách sách / độc giả nổi bật |
| 6 | Sẵn sàng tích hợp mở rộng | REST API đầy đủ — mobile app hay hệ thống khác kết nối được ngay |

**Ngoài phạm vi đề tài:** Thanh toán online · Đặt giữ sách trước · Gửi email nhắc nhở · Ứng dụng di động

**Visual Suggestion:**
Bảng 3 cột màu pastel — Mục tiêu | Giải pháp | ✓ Đã hoàn thành — icon check xanh lá từng dòng

---

## Slide 3 — Công nghệ sử dụng

### Tech Stack — Phân theo vai trò trong hệ thống

```
┌────────────────────────────────────────────────────┐
│  GIAO DIỆN NGƯỜI DÙNG                              │
│  TailwindCSS  ·  Alpine.js  ·  HTMX  ·  Chart.js  │
│  → Giao diện hiện đại, tìm kiếm tức thì,          │
│    biểu đồ thống kê trực quan                      │
├────────────────────────────────────────────────────┤
│  WEB SERVER & FRAMEWORK                            │
│  Python 3.12  ·  FastAPI  ·  Uvicorn               │
│  → Xử lý request nhanh, tự động sinh tài liệu API  │
├────────────────────────────────────────────────────┤
│  BẢO MẬT & XÁC THỰC                               │
│  JWT Token  ·  Bcrypt  ·  Pydantic v2              │
│  → Mã hoá mật khẩu, phiên đăng nhập an toàn        │
├────────────────────────────────────────────────────┤
│  CƠ SỞ DỮ LIỆU                                     │
│  SQLite  ·  SQLAlchemy ORM  ·  Alembic             │
│  → Lưu trữ dữ liệu, quản lý thay đổi schema       │
└────────────────────────────────────────────────────┘
```

**Lý do chọn công nghệ:**
- **FastAPI** — framework Python hiện đại, hiệu năng cao, tự sinh tài liệu API
- **HTMX** — tìm kiếm trực tiếp (live search) mà không cần tải lại trang
- **Chart.js** — biểu đồ thống kê đẹp, dễ đọc trên dashboard quản trị
- **SQLite** — phù hợp quy mô thư viện vừa, không cần cài đặt server riêng

**Visual Suggestion:**
Layer diagram 4 tầng — mỗi tầng một màu pastel khác nhau, tên công nghệ kèm logo, mũi tên luồng từ trên xuống

---

## Slide 4 — Tổng quan kiến trúc hệ thống

### Một server — Hai giao diện phục vụ độc lập

```
                    ┌──────────────────────────┐
                    │       NGƯỜI DÙNG         │
                    │   (Trình duyệt / App)    │
                    └────────┬─────────────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
    ┌─────────▼──────────┐    ┌─────────────▼──────────┐
    │    GIAO DIỆN WEB   │    │      REST API           │
    │                    │    │                         │
    │  Trang chủ · Sách  │    │  Dữ liệu JSON           │
    │  Quản trị · Độc giả│    │  Cho mobile / tích hợp  │
    │                    │    │  Tài liệu Swagger UI    │
    │  Đăng nhập: Cookie │    │  Đăng nhập: JWT Token   │
    └────────┬───────────┘    └────────────┬────────────┘
             └──────────────┬──────────────┘
                    ┌───────▼────────┐
                    │  Xử lý nghiệp  │
                    │     vụ         │  ← Toàn bộ quy tắc kinh doanh
                    └───────┬────────┘
                    ┌───────▼────────┐
                    │  Truy vấn dữ   │  ← Chỉ đọc / ghi dữ liệu
                    │    liệu        │
                    └───────┬────────┘
                    ┌───────▼────────┐
                    │   Cơ sở dữ     │
                    │    liệu        │
                    └────────────────┘
```

**Điểm nổi bật của kiến trúc:**
- Cùng một server phục vụ cả nhân viên thư viện (giao diện Web) lẫn hệ thống tích hợp (API)
- Quy tắc nghiệp vụ tập trung tại một nơi — không bị phân tán, dễ bảo trì
- Phân tách rõ ràng: tầng giao diện không chứa logic nghiệp vụ

**Visual Suggestion:**
Architecture diagram dọc, 2 nhánh Web/API hợp lại tại tầng nghiệp vụ — màu pastel, nhãn tiếng Việt rõ ràng

---

## Slide 5 — Cấu trúc dự án

### Tổ chức theo trách nhiệm — mỗi tầng một việc

```
Hệ thống chia thành 4 tầng rõ ràng:

┌─────────────────────────────────────────────────┐
│  TẦNG GIAO DIỆN                                 │
│  Web UI (HTML/Jinja2)  ·  REST API (JSON)        │
│  → Nhận yêu cầu từ người dùng, trả kết quả     │
├─────────────────────────────────────────────────┤
│  TẦNG NGHIỆP VỤ (Services)                      │
│  Xác thực · Mượn/Trả · Sách · Thống kê · ...   │
│  → Kiểm tra điều kiện, áp dụng quy tắc nghiệp  │
│    vụ trước khi thao tác dữ liệu                │
├─────────────────────────────────────────────────┤
│  TẦNG DỮ LIỆU (Repositories)                    │
│  Truy vấn người dùng · Sách · Phiếu mượn · ...  │
│  → Chỉ đọc/ghi database, không chứa logic      │
├─────────────────────────────────────────────────┤
│  TẦNG MÔ HÌNH (Models & Schemas)                │
│  5 Entities: User · Book · Category ·           │
│              Borrowing · Review                 │
│  → Định nghĩa cấu trúc dữ liệu, ràng buộc      │
└─────────────────────────────────────────────────┘
```

**Ý nghĩa của cách tổ chức này:**
- Tầng nghiệp vụ biết *khi nào* và *điều kiện gì* — tầng dữ liệu chỉ biết *cách lấy dữ liệu*
- Thêm tính năng mới không ảnh hưởng đến tầng khác
- Tái sử dụng: cùng một logic nghiệp vụ phục vụ cả Web lẫn API

**Visual Suggestion:**
4 khối màu pastel xếp dọc như tầng — mỗi tầng ghi rõ tên module thực tế, mũi tên luồng xử lý từ trên xuống

---

## Slide 6 — Thiết kế cơ sở dữ liệu

### 5 Bảng dữ liệu — Quan hệ và Toàn vẹn dữ liệu

```
      [Thể loại]
          │ 1
          │ N  (Xoá thể loại → sách vẫn còn, chỉ bỏ gán)
          ▼
       [Sách] ─────────────────────────────┐
          │ 1                              │ 1
          │ N  (Còn phiếu → CHẶN xoá)     │ N  (Xoá sách → xoá đánh giá)
          ▼                               ▼
    [Phiếu mượn]                     [Đánh giá]
          ▲ N                              ▲ N
          │  (Còn phiếu → CHẶN xoá)       │  (Xoá người dùng → xoá đánh giá)
          │ 1                              │ 1
       [Người dùng] ─────────────────────┘
```

**Các trường nghiệp vụ quan trọng:**

| Bảng | Trường đặc biệt | Ý nghĩa |
|---|---|---|
| Sách | Số lượng tổng / Số lượng còn sẵn | Tách biệt để theo dõi real-time |
| Phiếu mượn | Trạng thái (Đang mượn / Quá hạn / Đã trả) | Vòng đời phiếu mượn |
| Phiếu mượn | Tiền phạt / Đã thu chưa | Ghi nhận phạt và xác nhận thu tiền |
| Phiếu mượn | Số lần gia hạn | Giới hạn tối đa 2 lần |
| Phiếu mượn | Tình trạng sách khi trả | good / fair / poor / damaged |
| Đánh giá | Ràng buộc 1 đánh giá / người / sách | Mỗi độc giả chỉ review 1 lần |

**Chiến lược bảo vệ dữ liệu:**
- **Chặn xoá** — không thể xoá sách hoặc người dùng khi còn phiếu mượn chưa trả
- **Tự động dọn** — xoá sách thì xoá luôn đánh giá liên quan
- **Giữ nguyên** — xoá thể loại không ảnh hưởng đến sách

**Visual Suggestion:**
ERD diagram 5 bảng với đường quan hệ tô màu theo chiến lược: đỏ = chặn xoá · xanh = tự động xoá · xám = giữ nguyên; kèm cardinality 1–N rõ ràng

---

## Slide 7 — Business Logic Flow

### Quy trình nghiệp vụ cốt lõi

#### Quy trình 1 — Cấp phát sách cho Độc giả

```
Thủ thư tìm Độc giả          ← Tìm kiếm trực tiếp, kết quả hiện ngay
        │
        ▼
Thủ thư tìm Sách              ← Tìm kiếm trực tiếp, kết quả hiện ngay
        │
        ▼
Hệ thống kiểm tra tự động:
  ✓  Độc giả còn hoạt động?
  ✓  Sách còn bản có sẵn?
  ✓  Độc giả chưa vượt giới hạn 5 phiếu?
  ✓  Độc giả chưa đang mượn chính sách này?
        │
        ├── Không đạt → Thông báo lý do cụ thể, dừng lại
        │
        └── Đạt tất cả → Tạo phiếu mượn
                         Hạn trả = hôm nay + 14 ngày
                         Tồn kho tự động giảm 1
```

#### Quy trình 2 — Xử lý trả sách

```
Thủ thư chọn phiếu mượn
        │
        ▼
Ghi nhận tình trạng sách      ← Tốt / Còn dùng / Kém / Hư hỏng
        │
        ▼
Hệ thống tự tính phạt         ← Số ngày trễ × 5.000 VND
        │
        ▼
Xác nhận trả → Tồn kho tự động tăng 1
        │
        ▼
Thủ thư thu tiền phạt (nếu có) → Đánh dấu đã thanh toán
```

#### Quy trình 3 — Gia hạn

```
Độc giả hoặc Thủ thư yêu cầu gia hạn
        │
Kiểm tra: Chưa trả + Chưa gia hạn đủ 2 lần?
        │
        └── Đạt → Hạn trả tự động cộng thêm 14 ngày
```

#### Quy trình 4 — Đồng bộ sách quá hạn

```
Quản trị viên kích hoạt thủ công
        │
        ▼
Hệ thống quét toàn bộ phiếu: Đang mượn + Đã quá hạn ngày trả
        │
        ▼
Cập nhật trạng thái → Quá hạn · Tính lại tiền phạt tích luỹ
```

**Quy tắc nghiệp vụ cố định:**

| Quy tắc | Giá trị |
|---|---|
| Thời hạn mượn mặc định | 14 ngày |
| Tối đa gia hạn | 2 lần / phiếu |
| Tối đa phiếu đang mượn | 5 phiếu / độc giả |
| Phí phạt quá hạn | 5.000 VND / ngày |

**Visual Suggestion:**
Flowchart dọc Quy trình 1 — 4 hình thoi điều kiện (đỏ nhạt = không đạt / xanh = đạt); mini-flowchart Quy trình 2 đặt bên phải; bảng Quy tắc nghiệp vụ bên dưới

---

## Slide 8 — Roles & Phân quyền

### 3 Vai trò — Phân quyền rõ ràng theo chức năng

```
┌──────────────────────────────────────────────────────┐
│  QUẢN TRỊ VIÊN (Admin)                               │
│  Toàn quyền hệ thống                                 │
│  + Quản lý kho sách & thể loại                       │
│  + Quản lý tài khoản người dùng & vai trò            │
│  + Xem dashboard & báo cáo thống kê                  │
│  + Kích hoạt đồng bộ sách quá hạn                    │
├──────────────────────────────────────────────────────┤
│  THỦ THƯ (Librarian)                                 │
│  + Cấp phát sách cho độc giả (tìm kiếm trực tiếp)   │
│  + Xử lý trả sách & tính phạt tự động                │
│  + Xem và quản lý toàn bộ phiếu mượn                 │
│  + Xác nhận thu tiền phạt                            │
├──────────────────────────────────────────────────────┤
│  ĐỘC GIẢ (Reader)                                    │
│  + Tự đăng ký tài khoản                              │
│  + Duyệt & tìm kiếm sách (không cần đăng nhập)      │
│  + Xem sách đang mượn của mình                       │
│  + Tự gia hạn (tối đa 2 lần)                         │
│  + Viết đánh giá sách (sau khi đã mượn)              │
└──────────────────────────────────────────────────────┘
```

**Ma trận quyền:**

| Chức năng | Chưa đăng nhập | Độc giả | Thủ thư | Quản trị |
|---|---|---|---|---|
| Duyệt & tìm kiếm sách | ✓ | ✓ | ✓ | ✓ |
| Xem chi tiết sách + đánh giá | ✓ | ✓ | ✓ | ✓ |
| Xem & gia hạn phiếu của mình | — | ✓ | ✓ | ✓ |
| Viết đánh giá sách | — | ✓ | ✓ | ✓ |
| Cấp phát / xử lý trả sách | — | — | ✓ | ✓ |
| Xem tất cả phiếu mượn | — | — | ✓ | ✓ |
| Thêm / sửa / xóa sách | — | — | — | ✓ |
| Quản lý người dùng | — | — | — | ✓ |
| Xem dashboard & báo cáo | — | — | — | ✓ |

**Quy tắc đặc biệt:**
- Tài khoản bị khoá không thể đăng nhập — bị chặn ngay khi xác thực
- Độc giả chỉ nhìn thấy phiếu mượn của bản thân — không xem được người khác
- Không thể xoá sách hoặc người dùng khi còn phiếu mượn chưa trả

**Visual Suggestion:**
Ma trận quyền dạng bảng 5 cột màu — ô xanh pastel = có quyền · ô đỏ nhạt = không có quyền; phần header mỗi role dùng icon người tương ứng

---

## Slide 9 — Chức năng hệ thống & Giao diện

### 7 Nhóm chức năng — Phục vụ từng vai trò

**Dành cho tất cả (Public):**
- Trang chủ: thống kê nhanh số sách · số thể loại · sách nổi bật
- Danh sách sách: tìm kiếm theo tên / tác giả · lọc thể loại · phân trang
- Chi tiết sách: thông tin đầy đủ · ảnh bìa · điểm đánh giá trung bình · bình luận

**Dành cho Thủ thư:**
- Cấp phát sách: tìm kiếm độc giả và sách trực tiếp (gõ là hiện ngay, không reload)
- Xử lý trả: ghi tình trạng sách · hệ thống hiển thị tiền phạt tự động
- Quản lý phiếu: lọc theo trạng thái · độc giả · đang quá hạn

**Dành cho Quản trị viên:**
- Dashboard: KPI tổng quan · biểu đồ mượn/trả theo tháng · top sách & độc giả tích cực
- Quản lý kho sách: thêm / sửa / xoá sách · upload ảnh bìa · quản lý thể loại
- Quản lý người dùng: thay đổi vai trò · khoá / mở tài khoản

**Dành cho Độc giả:**
- Sách đang mượn: hạn trả · trạng thái · nút gia hạn ngay
- Lịch sử mượn toàn bộ · Cập nhật hồ sơ cá nhân

**Kênh tích hợp (Developers / Hệ thống ngoài):**
- REST API đầy đủ với tài liệu tự động (Swagger UI) — sẵn sàng cho mobile / third-party

**Visual Suggestion:**
```
┌──────────────────────┬──────────────────────┬──────────────────────┐
│   Admin Dashboard    │   Cấp phát sách       │   Danh sách sách     │
│  [KPI + Chart.js]    │  [Live search form]   │  [Search + filter]   │
├──────────────────────┼──────────────────────┼──────────────────────┤
│   Chi tiết sách      │   Xử lý trả sách      │   Swagger API Docs   │
│  [Ảnh + Đánh giá]   │  [Tiền phạt tự động]  │  [/api/docs]         │
└──────────────────────┴──────────────────────┴──────────────────────┘
```
*Screenshot grid 2×3 — ưu tiên Dashboard + Form cấp phát live search*

---

## Slide 10 — Kết luận, Hạn chế & Hướng phát triển

### Tổng kết đồ án

**Những gì đã hoàn thành:**
- Hệ thống Web hoàn chỉnh + REST API — một server phục vụ cả hai
- Phân quyền 3 cấp hoạt động đồng thời trên cả giao diện Web và API
- Quy trình lưu thông sách đầy đủ: Cấp phát · Trả sách · Gia hạn · Tính phạt · Đồng bộ quá hạn
- Dashboard quản trị: KPI · Biểu đồ theo tháng · Xếp hạng sách & độc giả
- Bộ kiểm thử tự động: 18 test cases bao phủ xác thực, quản lý sách, quy trình mượn/trả

**Hạn chế thực tế:**

| Hạn chế | Đánh giá |
|---|---|
| Cơ sở dữ liệu phù hợp quy mô vừa nhỏ | Tốt cho thư viện học thuật, cần nâng cấp khi scale |
| Đồng bộ quá hạn kích hoạt thủ công | Có thể tự động hoá bằng lịch chạy định kỳ |
| Chưa có thông báo email nhắc hạn | Tính năng phụ, không ảnh hưởng nghiệp vụ cốt lõi |
| Độc giả chưa tự đặt yêu cầu mượn | Luôn phải qua thủ thư — hướng cải thiện rõ ràng |

**Hướng phát triển:**

| Ngắn hạn | Trung hạn | Dài hạn |
|---|---|---|
| Nâng cấp database production | Hệ thống đặt giữ sách | Ứng dụng di động |
| Tự động đồng bộ quá hạn | Độc giả tự đặt yêu cầu mượn | Tích hợp thanh toán |
| Giới hạn tần suất truy cập API | Thông báo email nhắc hạn | Gợi ý sách thông minh |
| | Nhật ký thay đổi hệ thống | Triển khai Docker + CI/CD |

**Visual Suggestion:**
Trái — checklist "Đã hoàn thành" (5 dòng, icon check xanh) · Phải — Timeline roadmap 3 cột Ngắn / Trung / Dài hạn với màu gradient từ xanh nhạt đến xanh đậm

---

## Gamma Theme Configuration

```
Theme:         Custom
Primary:       #93C5FD  (pastel blue)
Secondary:     #BFDBFE  (light pastel blue)
Accent:        #1D4ED8  (deep blue — headings)
Background:    #F0F9FF  (ultra-light blue tint)
Text:          #1E293B  (dark slate)
Check/OK:      #86EFAC  (pastel green)
Block/Fail:    #FCA5A5  (pastel red)

Font:          Montserrat · Heading Large Bold · Body Medium
Layout:        Clean / Minimal · 16:9 Widescreen
Icons:         Outlined · Minimal
Diagrams:      Flowchart arrows · Pastel fills · No drop shadows
```

---

## Thứ tự Demo (nếu có thời gian trình bày trực tiếp)

1. **Trang chủ** — không cần đăng nhập, ấn tượng ngay từ đầu
2. **Form cấp phát sách** — gõ tên độc giả / sách → kết quả hiện ngay, không reload trang
3. **Admin Dashboard** — KPI tổng quan + biểu đồ hoạt động theo tháng
4. **Tài liệu API (Swagger UI)** — minh chứng REST API đầy đủ, sẵn sàng tích hợp

---

## Presentation Story Flow

```
Slide 1  — TẠI SAO   Bài toán thực tế → lý do cần số hoá
Slide 2  — CÁI GÌ    6 mục tiêu cụ thể đã được hiện thực
Slide 3  — CÔNG CỤ   Công nghệ → vai trò từng thành phần
Slide 4  — KIẾN TRÚC 1 server, 2 giao diện, phân tầng rõ ràng
Slide 5  — TỔ CHỨC   Cấu trúc dự án → phân tách trách nhiệm
Slide 6  — DỮ LIỆU   5 bảng, quan hệ, chiến lược bảo vệ dữ liệu
Slide 7  — NGHIỆP VỤ Quy trình mượn / trả / gia hạn / đồng bộ
Slide 8  — PHÂN QUYỀN 3 vai trò, ma trận quyền chi tiết
Slide 9  — DEMO      7 nhóm chức năng, giao diện thực tế
Slide 10 — KẾT LUẬN  Thành quả · Hạn chế trung thực · Roadmap
```
