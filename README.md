# Library Management System

A full-stack Library Management System built with **Python / FastAPI**, server-side rendered with **Jinja2 + HTMX + Alpine.js + TailwindCSS**. Migrated and redesigned from a PHP/Yii2 codebase.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Database & Migrations](#database--migrations)
- [Seeding Data](#seeding-data)
- [Running the App](#running-the-app)
- [URL Reference](#url-reference)
- [API Reference](#api-reference)
- [Running Tests](#running-tests)
- [Roles & Permissions](#roles--permissions)
- [Business Rules](#business-rules)

---

## Features

- **Book catalogue** — browse, search, filter by category / language / status
- **Borrowing workflow** — issue, return, renew, overdue tracking, fine calculation
- **Role-based access control** — Reader, Librarian, Admin
- **JWT authentication** — httponly cookie for web UI, Bearer token for REST API
- **Admin dashboard** — KPI cards, monthly borrowing chart (Chart.js), top books/readers
- **Book reviews** — star ratings + comments (readers who borrowed the book)
- **Category management** — inline add/edit/delete
- **User management** — role change, activate/deactivate
- **Live search** — HTMX partial page updates (no full reload)
- **Flash messages** — one-shot cookie, auto-dismiss
- **REST API** — full JSON API under `/api/v1/` with Swagger UI

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12+ (tested on 3.14) |
| Web framework | FastAPI |
| ASGI server | Uvicorn |
| ORM | SQLAlchemy 2.x (async) |
| Database | SQLite via aiosqlite |
| Migrations | Alembic |
| Auth | PyJWT + bcrypt |
| Validation | Pydantic v2 |
| Templating | Jinja2 (SSR) |
| Frontend interactivity | HTMX 1.9 (CDN) |
| Client-side UI | Alpine.js 3.x (CDN) |
| CSS | TailwindCSS CDN Play (JIT in browser) |
| Charts | Chart.js 4 (CDN) |
| Testing | pytest + pytest-asyncio + httpx |
| Linting | Ruff |

---

## Project Structure

```
source/
├── .env                        # Environment variables (git-ignored)
└── backend/
    ├── .env.example            # Template for .env
    ├── requirements.txt
    ├── alembic.ini
    ├── pytest.ini
    ├── seed.py                 # Database seeder
    ├── library.db              # SQLite database (auto-created)
    ├── alembic/
    │   └── versions/
    │       └── 001_initial_schema.py
    ├── tests/
    │   ├── conftest.py
    │   ├── test_auth.py
    │   ├── test_books.py
    │   └── test_borrowings.py
    └── app/
        ├── main.py             # App factory + lifespan
        ├── core/
        │   ├── config.py       # Settings (pydantic-settings, reads ../.env)
        │   └── security.py     # JWT + bcrypt helpers
        ├── db/
        │   ├── base.py         # DeclarativeBase
        │   └── session.py      # Async engine + session factory
        ├── models/             # SQLAlchemy ORM models
        ├── schemas/            # Pydantic v2 schemas
        ├── repositories/       # Async data-access layer
        ├── services/           # Business logic layer
        ├── dependencies/       # FastAPI dependency injection (API auth)
        ├── middleware/
        │   └── logging.py      # Request/response access log
        ├── api/v1/             # REST API routers (/api/v1/...)
        ├── web/                # Server-rendered web UI routers
        │   ├── auth.py         # /login, /register, /logout
        │   ├── site.py         # /, /books, /books/{id}
        │   ├── dependencies.py # Cookie-based auth dependencies
        │   ├── templating.py   # Jinja2 render() helper + flash
        │   ├── exceptions.py   # WebAuthRequired, WebForbidden
        │   ├── admin/          # /admin/* routes
        │   └── reader/         # /reader/* routes
        ├── templates/          # Jinja2 HTML templates
        │   ├── base.html       # Main layout (sidebar + navbar)
        │   ├── auth/
        │   ├── site/
        │   ├── books/
        │   ├── admin/
        │   ├── reader/
        │   ├── partials/       # HTMX fragments
        │   └── errors/
        ├── static/
        │   ├── css/app.css
        │   ├── js/app.js
        │   └── uploads/        # Uploaded book cover images
        └── utils/
```

---

## Getting Started

### Prerequisites

- Python 3.12 or higher
- `pip` (comes with Python)

### 1. Create & activate a virtual environment

```bash
# From the source/ directory
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# Windows CMD
.venv\Scripts\activate.bat

# Linux / macOS
source .venv/bin/activate
```

### 2. Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Configure environment

```bash
# Copy the example to source/.env  (one level above backend/)
copy backend\.env.example .env      # Windows
cp  backend/.env.example  .env      # Linux/macOS
```

Then open `.env` and set at minimum:

```
SECRET_KEY=<random 32+ character string>
ENVIRONMENT=development
```

---

## Environment Variables

The `.env` file lives at `source/.env` (one level above `backend/`).

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` |  | JWT signing key — use a long random string in production |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Access token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token lifetime |
| `DATABASE_URL` | `sqlite+aiosqlite:///./library.db` | SQLAlchemy async database URL |
| `ENVIRONMENT` | `production` | `development` enables auto table creation |
| `DEBUG` | `false` | Enables SQLAlchemy query logging |
| `BORROWING_PERIOD_DAYS` | `14` | Default loan period in days |
| `MAX_RENEWALS` | `2` | Maximum renewals per borrowing |
| `FINE_PER_DAY` | `5000.0` | Overdue fine in VND per day |
| `MAX_ACTIVE_BORROWINGS` | `5` | Max concurrent borrowings per reader |
| `ADMIN_USERNAME` | `admin` | Seeded admin account username |
| `ADMIN_EMAIL` | `admin@library.local` | Seeded admin account email |
| `ADMIN_PASSWORD` | `Admin@123456` | Seeded admin account password |
| `ALLOWED_ORIGINS` | `["http://localhost:3000"]` | CORS allowed origins (JSON array) |

---

## Database & Migrations

### Auto-creation (development)

When `ENVIRONMENT=development`, tables are created automatically on startup. No manual migration step is needed for a fresh start.

---

## Seeding Data

Populate the database with sample accounts, categories, books, borrowings, and reviews:

```bash
cd backend
python seed.py
```

**Default accounts:**

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `Admin@123456` |
| Librarian | `librarian1` | `Librarian@123` |
| Reader | `reader1` | `Reader@123456` |
| Reader | `reader2` | `Reader@123456` |

---

## Running the App

```bash
cd backend

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The server starts at **`http://localhost:8000`**.

---

## URL Reference

### Web UI

| URL | Description | Access |
|---|---|---|
| `GET /` | Home — stats + featured books | Public |
| `GET /books` | Browse & search all books | Public |
| `GET /books/{id}` | Book detail + reviews | Public |
| `GET /login` | Login form | Public |
| `GET /register` | Registration form | Public |
| `POST /logout` | Clear session cookie | Authenticated |
| `GET /reader/my-books` | Current active borrowings | Reader+ |
| `GET /reader/history` | Full borrowing history | Reader+ |
| `GET /reader/profile` | View & edit profile | Reader+ |
| `GET /reader/change-password` | Change password | Reader+ |
| `GET /admin/dashboard` | KPI dashboard + charts | Admin |
| `GET /admin/books` | Manage books | Librarian+ |
| `GET /admin/books/new` | Add new book | Admin |
| `GET /admin/books/{id}/edit` | Edit book | Admin |
| `GET /admin/borrowings` | View all borrowings | Librarian+ |
| `GET /admin/borrowings/issue` | Issue book to reader | Librarian+ |
| `GET /admin/borrowings/{id}/return` | Process book return | Librarian+ |
| `GET /admin/categories` | Manage categories | Admin |
| `GET /admin/users` | Manage users | Admin |

### Developer

| URL | Description |
|---|---|
| `http://localhost:8000/api/docs` | Swagger UI |
| `http://localhost:8000/api/redoc` | ReDoc |
| `http://localhost:8000/health` | Health check |

---

## API Reference

All REST endpoints are prefixed `/api/v1/`. Authentication uses `Authorization: Bearer <token>`.

Obtain a token via `POST /api/v1/auth/login` with `username` and `password` form fields (OAuth2 password flow).

| Resource | Endpoints |
|---|---|
| Auth | `POST /auth/login`, `/auth/register`, `/auth/refresh`, `/auth/change-password`, `GET /auth/me` |
| Books | `GET/POST /books`, `GET/PATCH /books/{id}`, `DELETE /books/{id}` |
| Categories | `GET/POST /categories`, `GET/PATCH /categories/{id}`, `DELETE /categories/{id}` |
| Borrowings | `GET/POST /borrowings`, `GET /borrowings/{id}`, `POST /borrowings/{id}/return`, `/renew`, `/mark-fine-paid` |
| Reviews | `GET/POST /reviews`, `PATCH /reviews/{id}`, `PATCH /reviews/{id}/status`, `DELETE /reviews/{id}` |
| Users | `GET/POST /users`, `GET/PATCH /users/me`, `GET/PATCH/DELETE /users/{id}` |
| Dashboard | `GET /dashboard/stats`, `/popular-books`, `/active-readers`, `/monthly-stats` |

---

## Running Tests

```bash
cd backend
pytest -v
```

Test coverage: auth (register/login/JWT), books (CRUD, RBAC, validation), borrowings (issue/return, renewal limits, availability).

---

## Roles & Permissions

| Action | Reader | Librarian | Admin |
|---|---|---|---|
| Browse books / view detail | X | X | X |
| View own borrowings | X | X | X |
| Renew own borrowing | X | X | X |
| Issue / return books | — | X | X |
| View all borrowings | — | X | X |
| Create / edit books | — | — | X |
| Delete books | — | — | X |
| Manage categories | — | — | X |
| Manage users | — | — | X |
| View dashboard | — | — | X |

---

## Business Rules

- **Loan period:** 14 days (configurable via `BORROWING_PERIOD_DAYS`)
- **Max renewals:** 2 per borrowing (configurable via `MAX_RENEWALS`)
- **Max concurrent borrowings:** 5 per reader (configurable via `MAX_ACTIVE_BORROWINGS`)
- **Overdue fine:** 5,000 VND per day (configurable via `FINE_PER_DAY`)
- **Reviews:** A reader must have borrowed the book at least once to leave a review
- **Delete book:** Blocked if the book has active (unreturned) borrowings
