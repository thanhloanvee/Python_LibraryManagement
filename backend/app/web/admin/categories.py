"""Admin category management."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.services.category import CategoryService
from app.web.dependencies import require_admin
from app.web.templating import render, set_flash

router = APIRouter()


@router.get("/admin/categories")
async def categories_index(
    request: Request,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    categories, total = await CategoryService(db).list_categories()
    return render(
        "admin/categories/index.html",
        {"categories": categories, "total": total},
        request,
    )


@router.post("/admin/categories")
async def category_create(
    name: str = Form(...),
    description: str = Form(default=""),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    try:
        await CategoryService(db).create_category(
            CategoryCreate(name=name, description=description or None)
        )
        resp = RedirectResponse(url="/admin/categories", status_code=302)
        set_flash(resp, f"Thể loại '{name}' đã được tạo.", "success")
        return resp
    except Exception as exc:
        resp = RedirectResponse(url="/admin/categories", status_code=302)
        set_flash(resp, str(exc.detail if hasattr(exc, "detail") else exc), "error")
        return resp


@router.post("/admin/categories/{category_id}/edit")
async def category_update(
    category_id: int,
    name: str = Form(...),
    description: str = Form(default=""),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    try:
        await CategoryService(db).update_category(
            category_id,
            CategoryUpdate(name=name, description=description or None),
        )
        resp = RedirectResponse(url="/admin/categories", status_code=302)
        set_flash(resp, f"Thể loại '{name}' đã được cập nhật.", "success")
        return resp
    except Exception as exc:
        resp = RedirectResponse(url="/admin/categories", status_code=302)
        set_flash(resp, str(exc.detail if hasattr(exc, "detail") else exc), "error")
        return resp


@router.post("/admin/categories/{category_id}/delete")
async def category_delete(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    try:
        cat = await CategoryService(db).get_or_404(category_id)
        name = cat.name
        await CategoryService(db).delete_category(category_id)
        resp = RedirectResponse(url="/admin/categories", status_code=302)
        set_flash(resp, f"Thể loại '{name}' đã được xóa.", "success")
        return resp
    except Exception as exc:
        resp = RedirectResponse(url="/admin/categories", status_code=302)
        set_flash(resp, str(exc.detail if hasattr(exc, "detail") else exc), "error")
        return resp
