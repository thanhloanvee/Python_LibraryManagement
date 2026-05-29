# DEFENSE_NOTES.md — Library Management System
## Phase 3 Part A: Project Limitation Review

> Tài liệu này tổng hợp các hạn chế thực tế của hệ thống, các cải tiến tiềm năng,
> và những điểm không nên nhấn mạnh quá mức trong buổi bảo vệ.

---

## 1. Project Limitations

### Hạn chế kỹ thuật

| # | Hạn chế | Biểu hiện trong code | Ảnh hưởng |
|---|---|---|---|
| 1 | **SQLite không phù hợp cho production** | `database_url = "sqlite+aiosqlite:///./library.db"` — single file, không hỗ trợ concurrent writes | Tốt cho học thuật, sẽ gặp bottleneck khi có nhiều user đồng thời |
| 2 | **Không có background job tự động** | `sync_overdue_statuses()` chỉ chạy khi Admin kích hoạt thủ công hoặc gọi qua API | Trạng thái OVERDUE không cập nhật tự động theo thời gian thực; cron job chưa được tích hợp vào app |
| 3 | **Refresh token không được lưu trữ/revoke** | `create_refresh_token()` chỉ ký JWT, không lưu vào DB → không thể invalidate khi logout | Refresh token bị lộ vẫn có thể dùng trong 7 ngày (hết hạn theo `refresh_token_expire_days`) |
| 4 | **TailwindCSS qua CDN Play (JIT)** | Template dùng CDN: `https://cdn.tailwindcss.com` — runtime compilation | Không tối ưu cho production; tải thêm vài trăm KB JS cho mỗi lần load trang |
| 5 | **Ảnh bìa lưu trực tiếp trên server** | `app/static/uploads/` — đặt tên file theo ISBN | Không dùng cloud storage; mất file khi redeploy nếu không mount volume |
| 6 | **Không có rate limiting** | Không có giới hạn số lần gọi API | Endpoint `/api/v1/auth/login` và `/api/v1/auth/register` có thể bị brute-force |
| 7 | **Tự động tạo bảng thay vì chạy migration** | `main.py`: chỉ `create_all` trong môi trường `development`/`testing` | Migration Alembic (001_initial_schema.py) tồn tại nhưng không phải quy trình chính để khởi tạo DB trong dev |
| 8 | **Không có audit trail** | Không có bảng `audit_log` hay middleware ghi lại ai thay đổi gì | Không thể truy vết lịch sử chỉnh sửa dữ liệu quan trọng (ai tạo/xóa sách, ai thay đổi role) |

### Hạn chế nghiệp vụ

| # | Hạn chế | Giải thích |
|---|---|---|
| 1 | **Reader không tự mượn sách** | Flow mượn sách bắt buộc phải qua Librarian (`/admin/borrowings/issue`); Reader không có form tự nộp yêu cầu |
| 2 | **Không có reservation / đặt giữ sách** | Khi sách hết bản (`available_quantity = 0`), Reader không có cơ chế đặt chỗ trong hàng đợi |
| 3 | **Thanh toán tiền phạt offline** | `fine_paid` chỉ là boolean — thủ thư click "đánh dấu đã thanh toán"; không tích hợp payment gateway |
| 4 | **Không có thông báo tự động** | Không gửi email/SMS nhắc nhở hạn trả, cảnh báo sách quá hạn, hay xác nhận mượn/trả |
| 5 | **Phạt chỉ tính theo ngày** | `fine_amount = days_overdue × 5,000 VND` — đơn giản, không phân biệt weekend/ngày lễ hay mức phạt lũy tiến |
| 6 | **Không quản lý nhiều chi nhánh** | Hệ thống thiết kế cho một thư viện đơn lẻ; không có khái niệm branch/location cho sách |

### Hạn chế về test coverage

| # | Hạn chế | Chi tiết |
|---|---|---|
| 1 | **Test coverage hạn chế** | Chỉ có 18 test cases — tập trung vào auth, books, borrowings; không có tests cho dashboard, reviews, categories, web UI |
| 2 | **Không có test cho Web UI** | Toàn bộ Jinja2 templates (`/web/*` routes) không được cover bởi tests tự động |
| 3 | **Không test sync_overdue** | Business logic quan trọng `sync_overdue_statuses()` chưa có test case |

---

## 2. Potential Improvements

### Cải tiến kỹ thuật ngắn hạn (dễ thực hiện)

| Cải tiến | Hướng thực hiện |
|---|---|
| **Chuyển sang PostgreSQL** | Thay `sqlite+aiosqlite` bằng `postgresql+asyncpg`; cấu hình qua biến môi trường `DATABASE_URL` |
| **Tự động sync overdue** | Tích hợp `APScheduler` hoặc `FastAPI-Scheduler` để chạy `sync_overdue_statuses()` hằng đêm (ví dụ: 0:00 AM) |
| **Rate limiting** | Thêm `slowapi` (giới hạn request/phút trên endpoint auth) |
| **Refresh token blacklist** | Lưu `refresh_token` vào bảng `user_tokens` với trường `revoked`; xóa khi logout |
| **Build TailwindCSS** | Chuyển từ CDN sang `tailwindcss` CLI để generate file CSS tối ưu |
| **Cloud storage cho ảnh** | Tích hợp S3-compatible storage (AWS S3, Cloudflare R2, MinIO) thay vì local `uploads/` |

### Cải tiến nghiệp vụ trung hạn

| Cải tiến | Hướng thực hiện |
|---|---|
| **Hệ thống đặt giữ sách** | Thêm bảng `reservations` — reader đặt chỗ khi sách hết; tự động thông báo khi sách được trả |
| **Self-service borrowing request** | Reader tạo `BorrowingRequest`; Librarian approve/reject qua dashboard |
| **Email notifications** | Tích hợp `FastAPI-Mail` / SendGrid — gửi email xác nhận mượn, nhắc hạn trả 3 ngày trước |
| **Audit log** | Thêm `AuditLog` model ghi lại `(user_id, action, entity, entity_id, timestamp)` cho các thao tác quan trọng |
| **Phân trang trên Dashboard** | Hiện tại top sách/readers hard-code 5-10 items; thêm option chọn date range |

---

## 3. Future Enhancements

### Hướng phát triển dài hạn

| # | Enhancement | Mô tả |
|---|---|---|
| 1 | **Ứng dụng di động** | Tận dụng REST API hiện có (`/api/v1/`) để xây dựng app iOS/Android bằng React Native hoặc Flutter |
| 2 | **Hệ thống đề xuất sách** | Recommendation engine dựa trên lịch sử mượn và thể loại yêu thích của reader |
| 3 | **Tích hợp barcode/QR** | Scanner barcode ISBN khi mượn/trả để tăng tốc quy trình tại quầy |
| 4 | **Multi-branch support** | Mở rộng hệ thống quản lý nhiều chi nhánh thư viện, chuyển sách liên chi nhánh |
| 5 | **Thanh toán online** | Tích hợp VNPay / MoMo để reader thanh toán tiền phạt trực tuyến |
| 6 | **Reporting nâng cao** | Export báo cáo Excel/PDF; thống kê theo thể loại, mùa vụ, xu hướng đọc sách |
| 7 | **Containerization** | Đóng gói bằng Docker + Docker Compose; deploy lên cloud (Railway, Render, VPS) |
| 8 | **Full-text search nâng cao** | Tích hợp Elasticsearch hoặc Meilisearch để tìm kiếm nội dung sách, tìm kiếm mờ (fuzzy search) |

---

## 4. Topics That Should NOT Be Overemphasized During Presentation

### Tránh nhấn mạnh quá mức những điểm sau

| Chủ đề | Lý do |
|---|---|
| **SQLite trong production** | Đây là dự án học thuật — SQLite là lựa chọn hợp lý cho scope này. Không cần xin lỗi về SQLite; thay vào đó hãy trình bày rõ "phù hợp với quy mô thư viện nhỏ và môi trường học tập" |
| **Thiếu email notifications** | Đây là tính năng phụ, không ảnh hưởng đến core business flow. Mention như "future enhancement" là đủ |
| **Test coverage thấp** | Nếu hỏi, hãy trình bày những gì đã test (happy path, RBAC, business rules); không cần liệt kê những gì chưa test trừ khi bị hỏi cụ thể |
| **TailwindCSS CDN** | Chi tiết kỹ thuật này không có giá trị trình bày; nếu hỏi về performance thì mới đề cập |
| **Không có barcode scanner** | Tính năng tiện lợi nhưng không phải core requirement của đề tài quản lý thư viện |
| **Refresh token không có blacklist** | Chi tiết security nâng cao, nằm ngoài scope đề tài học thuật; chỉ đề cập nếu bị hỏi sâu về security |
| **Sync overdue thủ công** | Hãy trình bày là "có thể tích hợp cron job trong tương lai" thay vì nói đây là lỗ hổng |

### Điểm mạnh nên chủ động nhấn mạnh thay thế

| Thay vì nói về... | Hãy nhấn mạnh... |
|---|---|
| SQLite → chậm | FastAPI async → xử lý concurrent requests tốt |
| Thiếu email | HTMX live search → UX mượt mà, không reload trang |
| Test ít | Business rules được enforce chặt chẽ (5 validation checks khi mượn sách) |
| Không có reservation | Hệ thống kiểm tra `available_quantity` real-time tránh double-booking |
| Không có mobile app | REST API sẵn sàng — có thể tích hợp mobile sau |
