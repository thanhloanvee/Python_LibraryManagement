"""Category repository."""
from __future__ import annotations

from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category


class CategoryRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, category_id: int) -> Optional[Category]:
        result = await self._db.execute(
            select(Category).where(Category.id == category_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Category]:
        result = await self._db.execute(
            select(Category).where(Category.name == name)
        )
        return result.scalar_one_or_none()

    async def list_all(
        self,
        *,
        search: Optional[str] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> Tuple[List[Category], int]:
        query = select(Category)
        count_query = select(func.count(Category.id))

        if search:
            condition = Category.name.ilike(f"%{search}%")
            query = query.where(condition)
            count_query = count_query.where(condition)

        total = (await self._db.execute(count_query)).scalar_one()
        items = (
            await self._db.execute(
                query.order_by(Category.name.asc()).offset(offset).limit(limit)
            )
        ).scalars().all()
        return list(items), total

    async def create(self, category: Category) -> Category:
        self._db.add(category)
        await self._db.flush()
        await self._db.refresh(category)
        return category

    async def save(self, category: Category) -> Category:
        self._db.add(category)
        await self._db.flush()
        await self._db.refresh(category)
        return category

    async def delete(self, category: Category) -> None:
        await self._db.delete(category)
        await self._db.flush()
