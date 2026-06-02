"""Web auth routes: login, register, logout."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_db
from app.services.auth import AuthService
from app.schemas.auth import LoginRequest, RegisterRequest
from app.web.dependencies import get_optional_web_user
from app.web.templating import render, set_flash

settings = get_settings()
router = APIRouter(tags=["Web Auth"])


@router.get("/login")
async def login_page(
    request: Request,
    next: str = "/",
    user=Depends(get_optional_web_user),
):
    if user:
        return RedirectResponse(url="/", status_code=302)
    return render("auth/login.html", {"next": next}, request)


@router.post("/login")
async def login_submit(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    next: str = Form(default="/"),
    db: AsyncSession = Depends(get_db),
):
    try:
        service = AuthService(db)
        tokens = await service.login(LoginRequest(username=username, password=password))

        redirect_url = next if next.startswith("/") else "/"
        resp = RedirectResponse(url=redirect_url, status_code=302)
        resp.set_cookie(
            key="access_token",
            value=tokens.access_token,
            httponly=True,
            max_age=settings.access_token_expire_minutes * 60,
            samesite="lax",
            secure=settings.environment == "production",
        )
        resp.set_cookie(
            key="refresh_token",
            value=tokens.refresh_token,
            httponly=True,
            max_age=settings.refresh_token_expire_days * 86400,
            samesite="lax",
            secure=settings.environment == "production",
        )
        return resp
    except Exception:
        resp = render(
            "auth/login.html",
            {"error": "Invalid username or password.", "next": next},
            request,
        )
        return resp


@router.get("/register")
async def register_page(
    request: Request,
    user=Depends(get_optional_web_user),
):
    if user:
        return RedirectResponse(url="/", status_code=302)
    return render("auth/register.html", {}, request)


@router.post("/register")
async def register_submit(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(...),
    phone: str = Form(default=""),
    db: AsyncSession = Depends(get_db),
):
    errors: dict = {}
    try:
        service = AuthService(db)
        await service.register(
            RegisterRequest(
                username=username,
                email=email,
                password=password,
                full_name=full_name,
                phone=phone or None,
            )
        )
        resp = RedirectResponse(url="/login", status_code=302)
        set_flash(resp, "Đăng ký thành công! Vui lòng đăng nhập.", "success")
        return resp
    except Exception as exc:
        errors["general"] = str(exc.detail if hasattr(exc, "detail") else exc)
        return render(
            "auth/register.html",
            {
                "errors": errors,
                "form": {
                    "username": username,
                    "email": email,
                    "full_name": full_name,
                    "phone": phone,
                },
            },
            request,
        )


@router.post("/logout")
async def logout():
    resp = RedirectResponse(url="/login", status_code=302)
    resp.delete_cookie("access_token")
    resp.delete_cookie("refresh_token")
    return resp
