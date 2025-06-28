from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    model = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_one(self, data: dict):
        stmt = insert(self.model).values(**data).returning(self.model)
        res = await self.session.execute(stmt)
        return res.scalar_one().to_pydantic_model()

    async def get_by_id(self, obj_id: int):
        result = await self.session.execute(
            select(self.model).where(self.model.id == obj_id)
        )
        return result.scalar_one_or_none().to_pydantic_model()

    async def get_all(self) -> list:
        result = await self.session.execute(select(self.model))
        return result.scalars().all()

    async def delete(self, obj_id: int) -> None:
        obj = await self.get_by_id(obj_id)
        if obj:
            await self.session.delete(obj)
            await self.session.flush()
