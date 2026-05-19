"""FastAPI application factory."""
from __future__ import annotations

import logging
import logging.config
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine
from app.middleware.logging import LoggingMiddleware

import app.models  # noqa: F401

settings = get_settings()

BASE_DIR = Path(__file__).resolve().parent

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger("library")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle handler."""
    logger.info("Starting %s v%s", settings.app_name, settings.app_version)

    if settings.environment in ("development", "testing"):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables ensured (dev mode).")

    yield

    logger.info("Shutting down…")
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Library Management System REST API",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    static_dir = BASE_DIR / "static"
    static_dir.mkdir(exist_ok=True)
    (static_dir / "uploads").mkdir(exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(LoggingMiddleware)

    app.include_router(api_router)

    from app.web.router import web_router
    app.include_router(web_router)

    from app.web.exceptions import WebAuthRequired, WebForbidden

    @app.exception_handler(WebAuthRequired)
    async def handle_auth_required(request: Request, exc: WebAuthRequired):
        next_url = request.url.path
        return RedirectResponse(url=f"/login?next={next_url}", status_code=302)

    @app.exception_handler(WebForbidden)
    async def handle_forbidden(request: Request, exc: WebForbidden):
        from app.web.templating import render
        return render("errors/403.html", {}, request, status_code=403)

    @app.get("/health", tags=["Health"], include_in_schema=False)
    async def health():
        return {"status": "ok", "version": settings.app_version}

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception("Unhandled exception on %s %s", request.method, request.url)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An internal server error occurred."},
        )

    return app


app = create_app()
