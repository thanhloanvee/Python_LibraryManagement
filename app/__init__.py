"""
FastAPI application factory.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import create_tables
from app.utils.logger import setup_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup / shutdown tasks."""
    settings = get_settings()
    setup_logger(settings.LOG_LEVEL, settings.LOG_FILE)
    create_tables()
    yield  # app running here
    # shutdown cleanup (if needed)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="Library Management System",
        description=(
            "Advanced Library Management System API\n\n"
            "Use `/api/auth/login` to obtain a Bearer token, "
            "then click **Authorize** above and paste it."
        ),
        version="2.0.0",
        docs_url="/docs",        # Swagger UI
        redoc_url="/redoc",      # ReDoc
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ── CORS ──────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Static files ──────────────────────────────────────────────
    app.mount("/static", StaticFiles(directory="static"), name="static")

    # ── API routers ───────────────────────────────────────────────
    from app.routers import auth_router, user_router, book_router, borrow_router, report_router, frontend_router

    app.include_router(auth_router.router,     prefix="/api/auth")
    app.include_router(user_router.router,     prefix="/api/users")
    app.include_router(book_router.router,     prefix="/api/books")
    app.include_router(borrow_router.router,   prefix="/api/borrows")
    app.include_router(report_router.router,   prefix="/api/reports")
    app.include_router(frontend_router.router)   # HTML pages at /

    return app
