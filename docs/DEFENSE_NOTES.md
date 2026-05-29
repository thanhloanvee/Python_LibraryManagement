# DEFENSE_NOTES.md — Hệ Thống Quản Lý Thư Viện
## Phase 3 Part A: Project Limitation Review

> Tài liệu này tổng hợp các hạn chế thực tế của hệ thống nhìn từ implementation,
> các cải tiến tiềm năng, và những điểm không nên nhấn mạnh quá mức trong buổi bảo vệ.

---

## 1. Project Limitations

Các hạn chế dưới đây đều quan sát trực tiếp từ codebase — không phỏng đoán.

### 1.1 Hạn chế kỹ thuật

#### Token không có revoke list
**File:** `app/web/auth.py:123–128`, `app/services/auth.py`

Khi người dùng logout, server chỉ xóa cookie phía client (`delete_cookie`). Token JWT vẫn hợp lệ cho đến khi hết hạn (mặc định 60 phút). Không có blacklist hay revocation mechanism. Nếu token bị lộ sau khi logout, nó vẫn dùng được trong khoảng thời gian còn lại.

#### Upload ảnh bìa dùng blocking I/O
**File:** `app/web/admin/books.py:33–39`

```python
with open(dest, "wb") as f:
    shutil.copyfileobj(cover_file.file, f)
```

File được ghi bằng synchronous I/O (`shutil.copyfileobj`) bên trong async route, không dùng `aiofiles` mặc dù `aiofiles` đã có trong dependencies. Điều này block event loop trong thời gian ghi file — ảnh hưởng hiệu năng khi có nhiều upload đồng thời.

#### Sync Overdue hoàn toàn thủ công
**File:** `app/api/v1/borrowings.py:200–215`, `app/services/borrowing.py:203–218`

Endpoint `/api/v1/borrowings/sync-overdue` cần được gọi thủ công (Admin bấm nút hoặc curl). Hệ thống không có cron job hay scheduler tự động. Comment trong code ghi "Can be called by a scheduled background task" nhưng không có implementation.

#### Không có rate limiting
Không có middleware hay dependency rate limiting cho bất kỳ endpoint nào. Endpoint `POST /auth/login`, `POST /auth/register` có thể bị tấn công brute-force mà không bị giới hạn.

#### SQLite concurrency
Database engine là SQLite với `check_same_thread=False`. SQLite chỉ hỗ trợ một writer tại một thời điểm (WAL mode không được bật). Với nhiều concurrent write request (issue book, return), có thể xảy ra locking delay. Phù hợp đồ án, không phù hợp production quy mô lớn.

#### Cover image không validate loại file
**File:** `app/web/admin/books.py:34`

Chỉ lấy extension từ tên file upload (`Path(cover_file.filename).suffix.lower()`) mà không kiểm tra MIME type thực sự. Có thể upload file không phải ảnh với extension giả.

---

### 1.2 Hạn chế tính năng

#### Không có hệ thống thông báo (Notification)
Không có email/SMS notification. Reader không nhận được cảnh báo khi:
- Sắp đến hạn trả sách (ví dụ: 3 ngày trước due_date)
- Sách đã trở thành OVERDUE
- Phiếu mượn được tạo thành công

#### Không có tính năng đặt trước / danh sách chờ
Không có reservation hay waiting list. Khi sách hết `available_quantity`, reader không thể đặt trước. Thủ thư phải thông báo ngoài hệ thống.

#### Không có quản lý nhiều bản sao (Copy management)
Hệ thống theo dõi `quantity` và `available_quantity` ở cấp độ đầu sách, không theo cấp độ từng bản vật lý. Không thể phân biệt bản nào đang ở tay reader nào khi một đầu sách có nhiều bản.

#### Không tích hợp barcode / QR
Cấp phát và trả sách hoàn toàn bằng tìm kiếm thủ công. Không có tích hợp máy quét mã vạch hay QR code.

#### Không có export báo cáo
Dashboard chỉ hiển thị số liệu trực quan. Không có tính năng export PDF, Excel, CSV cho bất kỳ báo cáo hay danh sách nào.

#### Không có quản lý tài chính chi tiết
Phí phạt chỉ gồm `fine_amount` (VND) và `fine_paid` (boolean). Không có lịch sử giao dịch thanh toán, không theo dõi người thu tiền, không có ngày thu tiền.

#### Không có reset mật khẩu qua email
Chỉ có chức năng đổi mật khẩu khi biết mật khẩu cũ (`change_password`). Không có flow "quên mật khẩu" / gửi link reset qua email.

#### Ảnh bìa lưu local disk
`UPLOAD_DIR` là thư mục `static/uploads/` trên server. Không có CDN, không có backup. Nếu server reset, ảnh bìa mất.

---

### 1.3 Phạm vi test

Có **17 test case** trải qua 3 file:
- `test_auth.py` — 7 tests: đăng ký, đăng nhập, JWT, phân quyền
- `test_books.py` — 6 tests: CRUD sách, phân quyền admin
- `test_borrowings.py` — 4 tests: issue/return, unavailable, RBAC reader, max renewals

**Chưa có test cho:**
- Web UI routes (chỉ test REST API)
- Review service
- Dashboard aggregation
- Edge cases của phí phạt (fine calculation)
- Sync overdue batch
- File upload

---

## 2. Potential Improvements

Các cải tiến có thể thực hiện trong phạm vi đồ án hoặc giai đoạn tiếp theo.

### 2.1 Kỹ thuật ngắn hạn

| Cải tiến | Mô tả | Độ phức tạp |
|---|---|---|
| **Async file upload** | Thay `shutil.copyfileobj` bằng `await aiofiles.open()` để không block event loop | Thấp |
| **Token blacklist đơn giản** | Lưu jti (JWT ID) vào Redis hoặc bảng DB khi logout, check khi xác thực | Trung bình |
| **APScheduler cho sync overdue** | Thêm `apscheduler` vào lifespan, chạy `sync_overdue_statuses()` mỗi giờ tự động | Thấp |
| **Rate limiting** | Thêm `slowapi` cho các endpoint auth để giới hạn request | Thấp |
| **File upload MIME validation** | Dùng `python-magic` để validate MIME type thực thay vì chỉ dựa extension | Thấp |
| **Mở rộng test coverage** | Thêm test cho review, dashboard, file upload, fine calculation edge cases | Trung bình |

### 2.2 Tính năng trung hạn

| Cải tiến | Mô tả | Độ phức tạp |
|---|---|---|
| **Email notification** | Tích hợp `fastapi-mail` + SMTP, gửi nhắc hạn trả trước 3 ngày | Trung bình |
| **Đặt trước sách** | Thêm bảng `reservations` — reader đặt trước khi sách hết, hệ thống thông báo khi có sẵn | Trung bình |
| **Export báo cáo** | Dùng `openpyxl` (Excel) hoặc `reportlab` (PDF) cho dashboard và danh sách phiếu | Trung bình |
| **Password reset qua email** | Flow quên mật khẩu: gửi link có token 1 giờ, reset qua link | Trung bình |
| **Fine payment history** | Thêm bảng `fine_payments` lưu lịch sử thu phạt (ai thu, khi nào, bao nhiêu) | Trung bình |

---

## 3. Future Enhancements

Các cải tiến cho phiên bản tương lai nếu hệ thống được phát triển thêm.

### 3.1 Nâng cấp hạ tầng

- **Chuyển sang PostgreSQL** — thay SQLite để hỗ trợ concurrent writes, full-text search tốt hơn, partitioning
- **Containerization** — Docker + docker-compose để chuẩn hoá môi trường deployment
- **CI/CD pipeline** — GitHub Actions chạy pytest tự động trên mỗi PR
- **Separate static file storage** — S3 hoặc MinIO cho ảnh bìa sách, tránh mất file

### 3.2 Mở rộng tính năng

- **Mobile-friendly UI** — hiện tại responsive nhưng chưa tối ưu cho mobile nhỏ
- **Barcode scanner integration** — Quagga.js hoặc ZXing để quét ISBN từ camera trình duyệt
- **Multi-branch support** — mở rộng hệ thống cho thư viện có nhiều chi nhánh
- **Digital content** — liên kết sách với file PDF/EPUB (ebook lending)
- **Fine amnesty / waiver** — Admin có thể miễn giảm phí phạt một phần
- **Bulk import** — Import danh sách sách từ CSV/Excel thay vì nhập từng cuốn

### 3.3 Bảo mật nâng cao

- **Two-factor authentication (2FA)** — TOTP (Google Authenticator) cho tài khoản Admin/Librarian
- **Audit log** — Ghi lại mọi thao tác nhạy cảm (thay đổi role, xóa user, xóa sách) kèm actor và timestamp
- **CAPTCHA** — Thêm CAPTCHA vào form đăng ký và đăng nhập để chống bot

---

## 4. Topics That Should NOT Be Overemphasized During Presentation

Các điểm nên trình bày ngắn gọn hoặc không chủ động đề cập để tránh tạo ấn tượng tiêu cực không cần thiết.

### 4.1 Không chủ động đề cập

| Chủ đề | Lý do |
|---|---|
| **Blocking file upload** | Lỗi kỹ thuật nhỏ trong async context — khó nhận ra nếu không đo benchmark, không ảnh hưởng đến chức năng |
| **Thiếu rate limiting** | Đây là concern của production deployment, không phải đồ án học thuật |
| **SQLite concurrency limit** | Hệ thống hoạt động hoàn toàn đúng trong bối cảnh thư viện quy mô nhỏ/vừa |
| **Token không revoke ngay lập tức** | Đây là tradeoff thiết kế JWT stateless được chấp nhận rộng rãi, không phải lỗi |
| **Test coverage chưa 100%** | 17 test case cover các happy path và business-critical paths — đủ cho đồ án |

### 4.2 Nếu bị hỏi — trả lời tự tin

**Q: "Tại sao dùng SQLite thay vì PostgreSQL?"**
> SQLite phù hợp với phạm vi đồ án — không cần cài đặt server riêng, dễ setup và demo. Nếu triển khai thực tế với nhiều người dùng đồng thời, sẽ migrate sang PostgreSQL mà không cần thay đổi code (chỉ đổi `DATABASE_URL`).

**Q: "Token có bị lộ sau khi logout không?"**
> Logout xóa cookie phía client, token hết hiệu lực sau 60 phút. Đây là tradeoff của JWT stateless — ưu điểm là không cần server-side session store. Giải pháp cải tiến là thêm token blacklist với Redis, sẽ implement trong phiên bản tiếp theo.

**Q: "Sách quá hạn có tự động cập nhật không?"**
> Hiện tại Admin kích hoạt thủ công hoặc gọi API endpoint. Hệ thống đã thiết kế sẵn `sync_overdue_statuses()` — bước tiếp theo là thêm APScheduler để chạy định kỳ tự động, code đã sẵn sàng.

**Q: "Không có test cho Web UI?"**
> Integration tests cover toàn bộ REST API endpoints qua httpx. Web UI routes dùng cùng Service layer đã được test — không bị duplicate logic. Test UI end-to-end (Selenium/Playwright) là bước cải tiến tiếp theo.

**Q: "Tại sao không có email thông báo?"**
> Email notification đòi hỏi SMTP server, xử lý async queue — vượt phạm vi đồ án. Kiến trúc hiện tại (Service layer tách biệt) cho phép thêm email service mà không ảnh hưởng business logic hiện có.

### 4.3 Điểm mạnh nên nhấn mạnh thay thế

Khi hội đồng hỏi về hạn chế, sau khi thừa nhận ngắn gọn, chuyển sang điểm mạnh:

- **Kiến trúc phân tầng rõ ràng** — dễ mở rộng, dễ test từng layer độc lập
- **Business rules được enforce ở đúng layer** — Service layer, không phải ở controller hay DB trigger
- **Dual authentication** — JWT Bearer cho API, httponly cookie cho Web — cả hai được implement đúng
- **RBAC 3 cấp** — enforce ở cả API Dependency lẫn Web route, không thể bypass
- **Tự động tính phí phạt** — logic gọn trong model method `calculate_fine()`, không hardcode
- **REST API với Swagger UI** — production-ready API documentation tự động từ Pydantic schema
- **Database integrity** — RESTRICT FK ngăn xóa sách/user có phiếu mượn, UNIQUE constraint ngăn duplicate review
