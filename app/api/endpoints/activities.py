from fastapi import APIRouter, Depends

from app.api.endpoints.dependencies import verify_api_key
from app.api.schemas.activities import ActivityCreate, ActivityRead
from app.services.activities import ActivityService
from app.utils.unitofwork import UnitOfWork

router = APIRouter(
    prefix="/activities",
    tags=["Activities"],
    dependencies=[Depends(verify_api_key)]
)


async def get_activities_service(uow: UnitOfWork = Depends(UnitOfWork)) -> ActivityService:
    return ActivityService(uow)


@router.post("/", response_model=ActivityRead)
async def create_activity(activity: ActivityCreate, service: ActivityService = Depends(get_activities_service)):
    return await service.add_activity(activity)


@router.get("/", response_model=list[ActivityRead])
async def list_activities(service: ActivityService = Depends(get_activities_service)):
    return await service.get_all_activities()
