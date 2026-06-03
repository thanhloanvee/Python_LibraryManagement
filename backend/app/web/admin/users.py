"""Admin user management."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User, UserRole, UserStatus
from app.repositories.borrowing import BorrowingRepository
from app.schemas.user import UserAdminUpdate, UserCreate
from app.services.user import UserService
from app.web.dependencies import require_admin
from app.web.templating import render, set_flash

router = APIRouter()


@router.get("/admin/users")
async def users_index(
    request: Request,
    search: str = "",
    role: str | None = None,
    status: str | None = None,
    page: int = 1,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    status_val: UserStatus | None = None
    if status is not None and status != "":
        try:
            status_val = UserStatus(int(status))
        except (ValueError, KeyError):
            status_val = None

    users, total = await UserService(db).list_users(
        role=UserRole(role) if role else None,
        status=status_val,
        search=search or None,
        page=page,
        page_size=20,
    )
    ctx = {
        "users": users,
        "total": total,
        "page": page,
        "page_size": 20,
        "filters": {"search": search, "role": role, "status": status},
        "roles": list(UserRole),
        "statuses": list(UserStatus),
    }
    if request.headers.get("HX-Request"):
        return render("admin/users/_rows.html", ctx, request)
    return render("admin/users/index.html", ctx, request)


@router.get("/admin/users/{user_id}")
async def user_detail(
    user_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """View user detail."""
    user = await UserService(db).get_or_404(user_id)
    return render("admin/users/detail.html", {"user": user}, request)


@router.post("/admin/users/{user_id}/toggle-status")
async def toggle_user_status(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Activate or deactivate a user account."""
    svc = UserService(db)
    user = await svc.get_or_404(user_id)
    new_status = (
        UserStatus.INACTIVE if user.status == UserStatus.ACTIVE else UserStatus.ACTIVE
    )

    # Check if trying to deactivate self
    if new_status == UserStatus.INACTIVE and user_id == current_user.id:
        resp = RedirectResponse(url="/admin/users", status_code=302)
        set_flash(resp, "Không thể vô hiệu hóa tài khoản của chính mình.", "error")
        return resp

    # Check if deactivating and user has active borrowings
    if new_status == UserStatus.INACTIVE:
        borrow_repo = BorrowingRepository(db)
        active_count = await borrow_repo.count_active_for_user(user_id)
        if active_count > 0:
            resp = RedirectResponse(url="/admin/users", status_code=302)
            set_flash(
                resp,
                f"Không thể vô hiệu hóa tài khoản '{user.username}' vì có {active_count} phiếu mượn chưa hoàn thành.",
                "error",
            )
            return resp

    await svc.admin_update_user(user_id, UserAdminUpdate(status=new_status))
    resp = RedirectResponse(url="/admin/users", status_code=302)
    label = "đã kích hoạt" if new_status == UserStatus.ACTIVE else "đã vô hiệu hóa"
    set_flash(resp, f"Tài khoản '{user.username}' {label}.", "success")
    return resp


@router.post("/admin/users/{user_id}/change-role")
async def change_user_role(
    user_id: int,
    role: str = Form(...),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    try:
        svc = UserService(db)
        user = await svc.get_or_404(user_id)
        role_enum = UserRole(role)
        await svc.admin_update_user(user_id, UserAdminUpdate(role=role_enum))
        resp = RedirectResponse(url="/admin/users", status_code=302)
        set_flash(resp, f"Vai trò của '{user.username}' đã được cập nhật.", "success")
        return resp
    except ValueError:
        resp = RedirectResponse(url="/admin/users", status_code=302)
        set_flash(resp, f"Vai trò không hợp lệ: {role}.", "error")
        return resp
