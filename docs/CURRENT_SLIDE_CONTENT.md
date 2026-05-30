# SLIDE CONTENT — Library Management System (LMS)

> Two source files:
> - **File A**: `Python_LMS_Slides.pptx` — Final presentation (16 slides)
> - **File B**: `Draft-LMS-Slides.pptx` — Draft version (10 slides)

---

## FILE A — Python_LMS_Slides.pptx

---

# Slide 1

**Title:** Hệ thống Quản lý Thư viện – Library Management System

**Purpose:** Cover / title slide — introduces the project, tech stack, and team members.

**Content:**
- Subject: Kỹ thuật lập trình Python
- Framework: FastAPI + SQLAlchemy 2.0
- Database: SQLite + Alembic
- Team:
  - Lê Thị Thanh Loan — 24210228
  - Trần Hưng Khoa — 24210220

---

# Slide 2

**Title:** Giới thiệu đề tài (Project Introduction)

**Purpose:** Define the problem, project goals, and target user roles.

**Content:**

**Bài toán (Problem):**
- Manual library management → error-prone
- Difficult to track borrowed/returned books
- No clear role-based access control
- No effective statistics

**Mục tiêu (Goals):**
- Digitize the entire library workflow
- Dual interface: REST API + Web UI
- 3-tier RBAC: Admin / Librarian / Reader
- Real-time statistics dashboard

**Đối tượng (Target Users):**
- Admin — full system administration
- Librarian — manage books & borrow/return
- Reader — browse books, borrow, write reviews

---

# Slide 3

**Title:** Chức năng chính (Core Features)

**Purpose:** Overview of the four main feature modules.

**Content:**

| Module | Features |
|---|---|
| **Quản lý Sách** | Add/Edit/Delete books; cover image upload; category management; search & filter (title, author, ISBN) |
| **Mượn / Trả** | Borrow → auto-deduct inventory; return confirmation + fine calculation; max 2 renewals; overdue tracking |
| **Quản lý Người dùng** | Register/Login; 3-role access; lock/activate accounts; change password |
| **Đánh giá & Thống kê** | 1–5 star rating + comments; admin dashboard; monthly stats; top borrowed books |

---

# Slide 4

**Title:** Công nghệ sử dụng (Technology Stack)

**Purpose:** Detail each technology, version, and its role in the system.

**Content:**

| Technology | Version | Role |
|---|---|---|
| FastAPI | 0.111+ | Web framework — REST API + HTML routing |
| SQLAlchemy 2.0 | 2.0 async | ORM — Python class ↔ DB table mapping |
| SQLite | latest | Database — async, lightweight, no separate server |
| Pydantic v2 | 2.8+ | Validation schema — validate input/output DTOs |
| PyJWT + bcrypt | latest | Authentication — JWT token + password hashing |
| Jinja2 | 3.x | Template engine — server-side HTML rendering |
| Alembic | 1.x | Database migration — schema version management |

---

# Slide 5

**Title:** Kiến trúc Hệ thống (System Architecture)

**Purpose:** Illustrate the 3-layer architecture and HTTP request flow.

**Content:**

**Layers:**
1. **Presentation Layer** — Jinja2 Templates (HTML/CSS/JS) + REST API (JSON) → `/templates/` + `/static/`
2. **Business Logic Layer** — FastAPI Routers → Services → Repositories → `/api/v1/` + `/web/` → `/services/` → `/repositories/`
3. **Data Layer** — SQLAlchemy ORM (AsyncSession) + aiosqlite (SQLite) → `/models/` + `/db/session.py`

**Request Flow:**
```
Browser / API Client
    ↓ HTTP Request
FastAPI App (main.py)
    ↓ Middleware (CORS, Logging)
Router → Service
    ↓ Business Logic
Repository → SQLite DB
    ↑ ORM Response
JSON / Jinja2 HTML
```

---

# Slide 6

**Title:** Mô hình Model-View-Controller (MVC Pattern)

**Purpose:** Map MVC roles to actual source files in the project.

**Content:**

| Layer | Source Files | Responsibility |
|---|---|---|
| **Model** | `models/user.py`, `models/book.py`, `models/borrowing.py`, `models/review.py`, `models/category.py` | SQLAlchemy ORM, business properties, validation rules |
| **View** | `templates/base.html`, `templates/admin/*`, `templates/reader/*`, `templates/auth/*` | Jinja2 HTML templates, server-side rendering, CSS + JS static files |
| **Controller** | `api/v1/*.py` (JSON), `web/admin/*.py`, `web/reader/*.py`, `dependencies/rbac.py` | FastAPI routers, request handling, response mapping |

---

# Slide 7

**Title:** Tổ chức mã nguồn (Code Structure)

**Purpose:** Show the project directory structure and explain the role of each module.

**Content:**

**Directory Structure:**
```
backend/
├── app/
│   ├── main.py
│   ├── core/          (config, security)
│   ├── db/            (session, base)
│   ├── models/
│   ├── schemas/
│   ├── repositories/
│   ├── services/
│   ├── api/v1/
│   ├── web/admin|reader/
│   ├── dependencies/
│   ├── middleware/
│   └── templates|static/
├── alembic/
└── tests/
```

**Module Roles:**

| Module | Role |
|---|---|
| `models/` | ORM entities: User, Book, Borrowing, Review, Category |
| `schemas/` | Pydantic DTOs — validate request/response |
| `repositories/` | DB queries — CRUD abstraction layer |
| `services/` | Business logic — BorrowingService, BookService, etc. |
| `api/v1/` | REST endpoints — return JSON + JWT auth |
| `web/` | Web UI endpoints — render HTML templates |
| `dependencies/` | `auth.py` (JWT) + `rbac.py` (role check) |
| `core/security.py` | bcrypt hash + JWT create/verify |

---

# Slide 8

**Title:** Data Model / ERD

**Purpose:** Present the database schema and entity relationships.

**Content:**

**Entities:**

| Entity | Key Fields |
|---|---|
| **Book** | id (PK), title, author, ISBN, quantity, available_quantity, cover_image |
| **User** | id (PK), username, email, hashed_password, role (enum), status (enum), full_name |
| **Borrowing** | id (PK), user_id (FK), book_id (FK), borrow_date, due_date, return_date, renewals, fine_amount |
| **Review** | id (PK), user_id (FK), book_id (FK), rating (1–5), comment, created_at |

**Relationships:**
- Book → Borrowing: 1 : N
- Book → Review: 1 : N
- User → Borrowing: 1 : N
- User → Review: 1 : N

---

# Slide 9

**Title:** Controller Layer — API Flow

**Purpose:** Walk through the borrow book API flow step-by-step and list all main endpoints.

**Content:**

**Borrow Flow (POST /api/v1/borrowings):**
1. User action → POST /api/v1/borrowings
2. `require_librarian` (RBAC check)
3. Validate user exists & is ACTIVE
4. Validate book exists
5. Check `book.is_available` (qty > 0)
6. Check user has not exceeded 5 active borrows
7. Calculate `due_date` = today + 14 days
8. `book.available_quantity -= 1`
9. INSERT Borrowing record (DB)
10. Return `BorrowingRead` (JSON)

**Main API Endpoints:**

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/auth/login` | Public | Login → JWT |
| GET | `/books` | Public | Book list |
| POST | `/books` | Librarian+ | Add new book |
| PUT | `/books/{id}` | Librarian+ | Update book |
| DELETE | `/books/{id}` | Admin | Delete book |
| POST | `/borrowings` | Librarian+ | Create borrow record |
| PATCH | `/borrowings/{id}/return` | Librarian+ | Return book |
| POST | `/borrowings/{id}/renew` | Librarian+ | Renew borrow |
| POST | `/reviews` | Reader+ | Submit review |
| GET | `/dashboard/stats` | Admin | Statistics |

---

# Slide 10

**Title:** Bảo mật & Phân quyền (Security & RBAC)

**Purpose:** Detail security techniques used and explain the RBAC role hierarchy.

**Content:**

**Security Techniques:**

| Technique | Detail |
|---|---|
| bcrypt 4.x | Password hashing + auto salt (no plain text stored) |
| JWT (PyJWT) | Access token 60 min + Refresh token 7 days |
| SQLAlchemy ORM | Parameterized queries → SQL Injection prevention |
| Pydantic v2 | Validate type, length, range at schema layer |
| CORSMiddleware | Whitelist `allowed_origins` from config |
| itsdangerous | Signed cookie session — tamper prevention |

**JWT Auth Flow:**
```
POST /auth/login → validate credentials
→ bcrypt.verify(password, hash)
→ create access_token (JWT, 60min)
→ create refresh_token (JWT, 7d)
→ Client stores token → sends with every request
→ Dependency get_current_user decodes JWT
→ Check UserStatus.ACTIVE
✓ Inject user object into route handler
```

**RBAC Role Hierarchy:** `READER ⊂ LIBRARIAN ⊂ ADMIN`

| Role | Permissions |
|---|---|
| Reader | View books, borrow online, view history, write reviews, change password |
| Librarian | Reader + Add/edit books & categories, process borrow/return/renewal, manage readers |
| Admin | Librarian + Delete books/users, view statistics dashboard, full system administration |

---

# Slide 11

**Title:** Demo

**Purpose:** Transition slide before the live demo session.

**Content:**
- *(No body content — demo placeholder)*

---

# Slide 12

**Title:** Demo Giao diện (UI Demo)

**Purpose:** Showcase the main UI screens of the application.

**Content:**

| Screen | Key UI Elements |
|---|---|
| **Login Page** | Email/Username field, Password field, Login button, Forgot password link |
| **Admin Dashboard** | Total books: 150 · Readers: 42 · Active borrows: 28 · Overdue: 3 |
| **Book Management** | Add book button, Search bar, Category filter, Book list with Edit/Delete |
| **Borrow/Return** | Select reader, Select book, 14-day due date, Confirm borrow button |
| **Borrow History** | Filter: Active / Returned; Overdue indicator; Fine: 10,000 VND; Confirm return |
| **Book Reviews** | ★★★★☆ (4.2/5), Comment: "Rất hay!", Write review, Total: 12 reviews |

---

# Slide 13

**Title:** Hạn chế Hệ thống (System Limitations)

**Purpose:** Honestly acknowledge current technical limitations of the system.

**Content:**

| # | Limitation | Description |
|---|---|---|
| ⚡ | SQLite not production-ready | No write concurrency — multiple simultaneous writes cause conflicts |
| 🛡️ | No Rate Limiting | No login attempt limit → vulnerable to brute-force attacks |
| 📧 | No Email Notifications | No due-date reminders or registration confirmations via email |
| 📱 | UI not fully responsive | Basic Jinja2 template, not optimized for mobile devices |
| 🔒 | Missing CSRF Protection | HTML form submissions lack CSRF tokens — risk for Web UI |
| 🗑️ | No Soft Delete | Deleting a book with active borrows can cause data integrity errors |

---

# Slide 14

**Title:** Hướng Phát triển (Development Roadmap)

**Purpose:** Outline a 3-phase roadmap for future improvements.

**Content:**

**Phase 1 — Immediate Improvements:**
- Replace SQLite with PostgreSQL (asyncpg)
- Add rate limiting (slowapi)
- Add CSRF tokens for HTML forms
- Implement soft delete for Book & User

**Phase 2 — Feature Expansion:**
- Email notifications (due-date reminders)
- Redis cache (dashboard + search)
- Excel/PDF report export
- Book reservation queue

**Phase 3 — Production Ready:**
- Docker + CI/CD pipeline
- Mobile app (React Native / Flutter)
- AI book recommendation engine
- Responsive UI redesign

---

# Slide 15

**Title:** Tổng kết (Summary)

**Purpose:** Recap completed deliverables and key learning outcomes.

**Content:**

**Completed:**
- ✓ Full REST API + dual Web UI interface
- ✓ Clear 3-layer modular architecture
- ✓ 3-role RBAC: Admin / Librarian / Reader
- ✓ Business rules: borrow / return / fine / renewal
- ✓ JWT auth + bcrypt + SQLAlchemy async ORM
- ✓ Statistics dashboard + Search & Filter

**Key Learnings:**
- ✓ FastAPI async programming patterns
- ✓ SQLAlchemy 2.0 ORM with AsyncSession
- ✓ JWT authentication & RBAC design
- ✓ Pydantic v2 validation & schema design
- ✓ Alembic database migration workflow
- ✓ Layered architecture best practices

---

# Slide 16

**Title:** Cảm ơn (Thank You)

**Purpose:** Closing slide.

**Content:**
- "Cảm ơn thầy và các bạn đã lắng nghe!"
- "Thank You"

---
---

## FILE B — Draft-LMS-Slides.pptx

---

# Slide 1

**Title:** Hệ thống Quản lý Thư viện – Library Management System

**Purpose:** Cover slide — draft version with a more detailed subtitle description.

**Content:**
- Subtitle: "Ứng dụng Web Python Hiện Đại cho Quản Lý Thư Viện"
- Tagline highlights:
  - Book catalog management, borrow/return workflow, reader accounts
  - Role-based access control: Reader → Librarian → Admin
  - Full-stack solution: REST API + Web UI (Server-rendered)
  - Built from the ground up with Python — async, layered architecture
- Team:
  - Lê Thị Thanh Loan — 24210228
  - Trần Hưng Khoa — 24210220

---

# Slide 2

**Title:** Mục tiêu và chức năng hệ thống (Goals & Features)

**Purpose:** Define the system vision and walk through the three core user workflows.

**Content:**

> "Xây dựng nền tảng quản lý thư viện có khả năng mở rộng, tinh gọn quy trình lưu thông và nâng cao trải nghiệm người dùng."

| Actor | Workflow |
|---|---|
| **Độc giả (Reader)** | Browse catalog → Request borrow → Librarian issues → Borrowing record created with 14-day due date |
| **Thủ thư (Librarian)** | Record return date → Calculate late fee (e.g., 2 days × 5,000 VND = 10,000 VND) → Update quantity |
| **Admin** | KPI dashboard, user management, role assignment, review moderation |

---

# Slide 3

**Title:** Công nghệ sử dụng (Technology Stack)

**Purpose:** Layer-based breakdown of the full tech stack.

**Content:**

| Layer | Technologies |
|---|---|
| **Backend** | Python 3.12+, FastAPI, Uvicorn, SQLAlchemy 2.x, SQLite + aiosqlite |
| **Frontend** | Jinja2, HTMX 1.9, TailwindCSS, Alpine.js 3.x, Chart.js 4 |
| **Security** | PyJWT + bcrypt, Pydantic v2, Alembic |

> Note: Draft stack adds **HTMX 1.9**, **TailwindCSS**, **Alpine.js**, **Chart.js** — not listed in the final slides.

---

# Slide 4

**Title:** Kiến trúc dự án (Project Architecture)

**Purpose:** Describe the layered architecture and each layer's responsibility.

**Content:**

**Architecture Flow:**
```
Browser (Client)
    ↓
FastAPI App (Web SSR+HTMX + REST API)
    ↓
Services → Repositories → ORM → SQLite
```

**Layer Responsibilities:**

| Layer | Responsibility |
|---|---|
| Models | Database schema (SQLAlchemy ORM) |
| Repositories | Data access layer (async queries) |
| Services | Business logic (validation, calculations, workflows) |
| Schemas | Pydantic DTOs for request/response |
| Dependencies | FastAPI dependency injection (auth, session) |
| API/Web Routes | HTTP endpoints (REST + SSR) |

> Principle: *Separation of Concerns* — each layer has a single, well-defined responsibility.

---

# Slide 5

**Title:** Môi trường thực nghiệm (Setup & Environment)

**Purpose:** Provide step-by-step setup instructions and seed account credentials for demo.

**Content:**

**Setup Steps:**
1. Clone repository; copy `.env.example` → `.env`
2. Install: `pip install -r requirements.txt`
3. Run migrations (auto-run on startup)
4. Seed sample data: `python seed.py`
5. Start server: `uvicorn app.main:app --reload`
6. Swagger UI: `http://localhost:8000/api/docs`

**Sample Accounts (seeded):**

| Username | Role | Password |
|---|---|---|
| admin | Admin | Admin@123456 |
| librarian1 | Librarian | Lib@123456 |
| reader1 | Reader | Reader@123 |

> Dataset: 20+ sample books · 5+ borrow/return records with varied statuses

---

# Slide 6

**Title:** Lược đồ ERD & Thiết kế CSDL (ERD & Database Design)

**Purpose:** Define the 5 main database entities and their purpose.

**Content:**

| Entity | Description |
|---|---|
| **users** | Reader/Librarian/Admin accounts with role enum |
| **books** | Book catalog with quantity tracking and BookStatus |
| **borrowings** | Tracks each borrow/return transaction; auto-calculates late fees |
| **categories** | Book classification (Fiction, Sci-Fi, History, etc.) |
| **reviews** | 1–5 star ratings; only users who have borrowed the book may review |

---

# Slide 7

**Title:** Các quy trình hệ thống cơ bản (Core Business Processes)

**Purpose:** Detail the three main transaction workflows.

**Content:**

| Process | Steps |
|---|---|
| **Mượn (Borrow)** | Librarian validates → Create record → Deduct quantity → 14-day due date |
| **Trả & Phí (Return & Fine)** | Record return date → Calculate 5,000 VND/day late fee → Mark unpaid fine → Increase quantity |
| **Gia hạn (Renewal)** | Reader requests → Check conditions (max 2 renewals, not overdue) → Extend +14 days |

> These three core workflows ensure transparent, automated borrow-return-fine management.

---

# Slide 8

**Title:** Hệ thống phân quyền (RBAC)

**Purpose:** Present the three user roles, their permissions, and the permission matrix.

**Content:**

**Role Definitions:**

| Role | Permissions |
|---|---|
| **Độc Giả (Reader)** | Browse catalog, search books, view personal borrow history, request renewal, submit reviews |
| **Thủ Thư (Librarian)** | Issue borrow & process return, record book condition, calculate fees, view all borrow records |
| **Quản Trị (Admin)** | Manage books/categories/users, moderate reviews, KPI dashboard, system reports |

**Permission Matrix:**

| Feature | Reader | Librarian | Admin |
|---|---|---|---|
| Browse book catalog | ✓ | ✓ | ✓ |
| Issue / Return books | ✗ | ✓ | ✓ |
| Manage books & categories | ✗ | ✗ | ✓ |
| Manage users | ✗ | ✗ | ✓ |
| Dashboard & Reports | ✗ | ✗ | ✓ |

---

# Slide 9

**Title:** Các chức năng và giao diện (Features & UI)

**Purpose:** Summarize the four main feature areas of the application.

**Content:**

| Feature | Description |
|---|---|
| **Quản Lý Sách** | Full catalog (ISBN, author, publisher); Available/Damaged/Lost status tracking; advanced search & filter |
| **Quy Trình Mượn/Trả** | Auto due-date calculation on issue; return processing with late fee; renewal management |
| **Hệ Thống Đánh Giá** | 1–5 star ratings, text comments, admin moderation before public display |
| **Admin Dashboard** | KPI overview, monthly borrow trend charts, top books & most active readers |

---

# Slide 10

**Title:** Tổng kết và Hướng phát triển (Summary & Roadmap)

**Purpose:** Recap achievements and list limitations with a future improvement roadmap.

**Content:**

**Achievements (✓):**
- Full-stack Python system built from the ground up with layered architecture
- Complete RBAC with a clear permission matrix
- Automated late fee calculation in borrow/return workflow
- Full REST API with Swagger/OpenAPI documentation
- Clean layered architecture, async-first, easy to scale

**Limitations & Future Improvements:**

| Area | Improvement |
|---|---|
| Database | SQLite → PostgreSQL for production |
| Security | Rate limiting middleware for API protection |
| Search | Elasticsearch for full-text search |
| Performance | Redis caching + Celery email notifications |
| Features | Book reservation with FIFO queue |
| Operations | Audit logging + i18n multilingual support |