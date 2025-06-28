from fastapi import APIRouter, Depends

from app.api.endpoints.dependencies import verify_api_key
from app.api.schemas.buildings import BuildingCreate, BuildingRead
from app.services.buildings import BuildingService
from app.utils.unitofwork import UnitOfWork

router = APIRouter(
    prefix="/buildings",
    tags=["Buildings"],
    dependencies=[Depends(verify_api_key)]
)


async def get_building_service(uow: UnitOfWork = Depends(UnitOfWork)) -> BuildingService:
    return BuildingService(uow)


@router.post("/", response_model=BuildingRead)
async def create_building(building: BuildingCreate, service: BuildingService = Depends(get_building_service)):
    return await service.add_building(building)


@router.get("/", response_model=list[BuildingRead])
async def list_buildings(service: BuildingService = Depends(get_building_service)):
    return await service.get_all_buildings()
