"""Main web router — aggregates all web sub-routers."""
from fastapi import APIRouter

from app.web.auth import router as auth_router
from app.web.site import router as site_router
from app.web.admin.dashboard import router as admin_dashboard_router
from app.web.admin.books import router as admin_books_router
from app.web.admin.borrowings import router as admin_borrowings_router
from app.web.admin.categories import router as admin_categories_router
from app.web.admin.users import router as admin_users_router
from app.web.reader.borrowings import router as reader_borrowings_router
from app.web.reader.profile import router as reader_profile_router

web_router = APIRouter()

web_router.include_router(auth_router)
web_router.include_router(site_router)
web_router.include_router(admin_dashboard_router)
web_router.include_router(admin_books_router)
web_router.include_router(admin_borrowings_router)
web_router.include_router(admin_categories_router)
web_router.include_router(admin_users_router)
web_router.include_router(reader_borrowings_router)
web_router.include_router(reader_profile_router)
