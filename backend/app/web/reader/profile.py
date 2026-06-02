"""Reader profile view/update."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.user import UserUpdate
from app.services.user import UserService
from app.web.dependencies import require_reader
from app.web.templating import render, set_flash

router = APIRouter()


@router.get("/reader/profile")
async def profile(
    request: Request,
    user=Depends(require_reader),
):
    return render("reader/profile.html", {"profile_user": user}, request)


@router.post("/reader/profile")
async def profile_update(
    request: Request,
    full_name: str = Form(...),
    phone: str = Form(default=""),
    address: str = Form(default=""),
    db: AsyncSession = Depends(get_db),
    user=Depends(require_reader),
):
    try:
        await UserService(db).update_profile(
            user.id,
            UserUpdate(full_name=full_name, phone=phone or None, address=address or None),
        )
        resp = RedirectResponse(url="/reader/profile", status_code=302)
        set_flash(resp, "Cập nhật hồ sơ thành công.", "success")
        return resp
    except Exception as exc:
        return render(
            "reader/profile.html",
            {
                "profile_user": user,
                "error": str(exc.detail if hasattr(exc, "detail") else exc),
            },
            request,
        )


@router.get("/reader/change-password")
async def change_password_page(request: Request, user=Depends(require_reader)):
    return render("reader/change_password.html", {}, request)


@router.post("/reader/change-password")
async def change_password_submit(
    request: Request,
    old_password: str = Form(...),
    new_password: str = Form(...),
    db: AsyncSession = Depends(get_db),
    user=Depends(require_reader),
):
    try:
        from app.schemas.auth import ChangePasswordRequest
        from app.services.auth import AuthService
        await AuthService(db).change_password(
            user,
            ChangePasswordRequest(old_password=old_password, new_password=new_password),
        )
        resp = RedirectResponse(url="/reader/profile", status_code=302)
        set_flash(resp, "Đổi mật khẩu thành công.", "success")
        return resp
    except Exception as exc:
        return render(
            "reader/change_password.html",
            {"error": str(exc.detail if hasattr(exc, "detail") else exc)},
            request,
        )
