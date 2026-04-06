# Library Management System

A full-featured Library Management System built with **FastAPI**, **SQLAlchemy**, and **SQLite**.  
Includes JWT authentication, role-based access control, borrow/return workflow, automatic fine calculation, reporting, a basic web UI, and interactive API docs (Swagger).

---

## Table of Contents

1. [Requirements](#requirements)
2. [Quick Start](#quick-start)
3. [Project Structure](#project-structure)
4. [Environment Variables](#environment-variables)
5. [API Overview](#api-overview)
6. [Roles & Permissions](#roles--permissions)
7. [Running Tests](#running-tests)
8. [Common Commands](#common-commands)

---

## Requirements

| Tool | Minimum version |
|------|----------------|
| Python | 3.10+ |
| pip | 23+ |

No Docker, PostgreSQL, or other external services are needed — **SQLite is used by default**.

---

## Quick Start

Follow these steps in order. Every command is run from the project root folder.

### 1. Clone / open the project

```bash
cd C:\Loan\Python\Python_LibraryManagement
```

### 2. Create a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

You will see `(venv)` at the start of your terminal prompt when the environment is active.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create the `.env` file

Copy the example file and edit it if needed (the defaults work for local development):

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

> **Important:** Change `JWT_SECRET_KEY` to any long random string before deploying.

### 5. Create the admin user

```bash
python seed.py
```

Output:

```
Admin user created successfully!
  Email   : admin@library.com
  Password: Admin1234
  Role    : admin

Swagger UI: http://127.0.0.1:5000/docs
```

### 6. Start the server

```bash
python main.py
```

Or with auto-reload during development:

```bash
uvicorn main:app --reload --port 5000
```

### 7. Open the app

| URL | Description |
|-----|-------------|
| http://127.0.0.1:5000/docs | **Swagger UI** — interactive API explorer |
| http://127.0.0.1:5000/redoc | ReDoc — alternative API docs |
| http://127.0.0.1:5000/ | Web UI (basic HTML frontend) |

### 8. Log in via Swagger

1. Open http://127.0.0.1:5000/docs
2. Find **POST /api/auth/login** → click **Try it out**
3. Enter:
   ```json
   {
     "email": "admin@library.com",
     "password": "Admin1234"
   }
   ```
4. Copy the `access_token` from the response
5. Click the **Authorize 🔒** button (top right) → paste the token → **Authorize**

All protected endpoints will now work.

---

## Project Structure

```
.
├── app/
│   ├── config.py          # Settings loaded from .env (Pydantic)
│   ├── database.py        # SQLAlchemy engine, session factory, Base
│   ├── models/            # ORM table definitions (User, Book, BorrowRecord, Fine)
│   ├── schemas/           # Pydantic request/response models
│   ├── repositories/      # Database query layer
│   ├── services/          # Business logic (auth, books, borrows, reports)
│   ├── routers/           # FastAPI route handlers
│   ├── dependencies/      # JWT auth + role checking (Depends)
│   ├── templates/         # Jinja2 HTML templates
│   └── utils/             # Logger, response helpers, pagination
├── tests/                 # pytest test suite (32 tests)
├── main.py                # Entry point — runs uvicorn
├── seed.py                # Creates the default admin account
├── requirements.txt
├── .env.example
└── pytest.ini
```

---

## Environment Variables

All settings live in `.env`. The table below explains each one:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./library.db` | Database connection string |
| `JWT_SECRET_KEY` | *(change this!)* | Secret used to sign JWT tokens |
| `JWT_ACCESS_TOKEN_EXPIRES_MINUTES` | `60` | Access token lifetime |
| `JWT_REFRESH_TOKEN_EXPIRES_DAYS` | `30` | Refresh token lifetime |
| `MAX_BORROW_LIMIT` | `5` | Max books a member can borrow at once |
| `BORROW_PERIOD_DAYS` | `14` | Days before a borrow is overdue |
| `FINE_PER_DAY` | `1.00` | Fine amount per overdue day (USD) |
| `LOG_LEVEL` | `DEBUG` | Logging verbosity (`DEBUG`/`INFO`/`WARNING`) |
| `LOG_FILE` | `logs/app.log` | Log output file path |

To use **PostgreSQL** instead of SQLite, change `DATABASE_URL`:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/library_db
```

---

## API Overview

All API routes are prefixed with `/api`.

| Method | Endpoint | Description | Min. Role |
|--------|----------|-------------|-----------|
| POST | `/api/auth/register` | Create a new account | — |
| POST | `/api/auth/login` | Login and get tokens | — |
| POST | `/api/auth/refresh` | Renew access token | — |
| GET | `/api/auth/me` | Current user profile | any |
| GET | `/api/books/` | List / search books | any |
| GET | `/api/books/{id}` | Book detail | any |
| POST | `/api/books/` | Add a book | librarian |
| PUT | `/api/books/{id}` | Update a book | librarian |
| DELETE | `/api/books/{id}` | Delete a book | admin |
| POST | `/api/borrows/` | Borrow a book | member |
| PATCH | `/api/borrows/{id}/return` | Return a book | member |
| GET | `/api/borrows/my` | My borrow history | any |
| GET | `/api/borrows/` | All borrows | librarian |
| GET | `/api/reports/summary` | System summary stats | admin |
| GET | `/api/reports/popular` | Most borrowed books | librarian |
| GET | `/api/reports/overdue` | Overdue borrows | librarian |
| GET | `/api/reports/members` | Member activity | librarian |
| GET | `/api/users/` | List all users | admin |
| PATCH | `/api/users/{id}/status` | Activate/deactivate user | admin |
| DELETE | `/api/users/{id}` | Delete a user | admin |

---

## Roles & Permissions

| Role | Description |
|------|-------------|
| **member** | Can borrow and return books. Default role on registration. |
| **librarian** | Can add/update books, view all borrows and reports. |
| **admin** | Full access — includes user management and delete operations. |

---

## Running Tests

```bash
# Run all 32 tests
pytest

# Run with verbose output
pytest -v

# Run a specific file
pytest tests/test_auth.py -v

# Run with coverage report
pytest --cov=app --cov-report=term-missing
```

Expected output: **32 passed**.

---

## Common Commands

```bash
# Activate virtual environment (run this every time you open a new terminal)
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS / Linux

# Start the server
python main.py

# Re-seed the admin user (safe to run multiple times)
python seed.py

# Run tests
pytest -v

# Deactivate virtual environment
deactivate
```
