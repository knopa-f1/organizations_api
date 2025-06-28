from app.api.schemas.buildings import BuildingCreate, BuildingRead
from app.utils.unitofwork import UnitOfWork


class BuildingService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def add_building(self, data: BuildingCreate) -> BuildingRead:
        async with self.uow:
            building = await self.uow.buildings.add_one(data.model_dump())
            await self.uow.commit()
            return building

    async def get_all_buildings(self) -> list[BuildingRead]:
        async with self.uow:
            buildings = await self.uow.buildings.get_all()
            return [BuildingRead.model_validate(b) for b in buildings]
