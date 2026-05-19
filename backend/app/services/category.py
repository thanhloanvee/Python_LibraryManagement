"""Category service."""
from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.repositories.category import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    def __init__(self, db: AsyncSession) -> None:
        self._repo = CategoryRepository(db)

    async def get_or_404(self, category_id: int) -> Category:
        cat = await self._repo.get_by_id(category_id)
        if not cat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )
        return cat

    async def list_categories(self, *, search=None, page=1, page_size=100):
        offset = (page - 1) * page_size
        return await self._repo.list_all(
            search=search, offset=offset, limit=page_size
        )

    async def create_category(self, data: CategoryCreate) -> Category:
        existing = await self._repo.get_by_name(data.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="This category name already exists.",
            )
        cat = Category(name=data.name, description=data.description)
        return await self._repo.create(cat)

    async def update_category(
        self, category_id: int, data: CategoryUpdate
    ) -> Category:
        cat = await self.get_or_404(category_id)
        if data.name is not None and data.name != cat.name:
            existing = await self._repo.get_by_name(data.name)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="This category name already exists.",
                )
            cat.name = data.name
        if data.description is not None:
            cat.description = data.description
        return await self._repo.save(cat)

    async def delete_category(self, category_id: int) -> None:
        cat = await self.get_or_404(category_id)
        await self._repo.delete(cat)
