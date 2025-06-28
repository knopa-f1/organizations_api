from fastapi import APIRouter, Depends, Query, HTTPException

from app.api.endpoints.dependencies import verify_api_key
from app.api.schemas.organizations import OrganizationCreate, OrganizationRead, OrganizationDetailRead
from app.services.organizations import OrganizationService
from app.utils.unitofwork import UnitOfWork

router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
    dependencies=[Depends(verify_api_key)]
)


async def get_organization_service(uow: UnitOfWork = Depends(UnitOfWork)) -> OrganizationService:
    return OrganizationService(uow)


@router.post("/", response_model=OrganizationRead)
async def create_organization(data: OrganizationCreate,
                              service: OrganizationService = Depends(get_organization_service)):
    return await service.add_organization(data)


@router.get("/search", response_model=OrganizationDetailRead)
async def search_organization(
        org_id: int | None = None,
        name: str | None = None,
        service: OrganizationService = Depends(get_organization_service),
):
    if org_id is not None:
        return await service.get_by_id(org_id)

    if name is not None:
        return await service.get_by_name(name)

    raise HTTPException(status_code=400, detail="Отсутствует параметр поиска: 'id' или 'name'")


@router.get("/list/", response_model=list[OrganizationDetailRead])
async def get_organizations(
        building_id: int | None = Query(None),
        activity_id: int | None = Query(None),
        service: OrganizationService = Depends(get_organization_service)
):
    return await service.get_filtered_organizations(building_id, activity_id)


@router.get("/by_activity/{activity_id}", response_model=list[OrganizationDetailRead])
async def orgs_by_activity_deep(
        activity_id: int,
        service: OrganizationService = Depends(get_organization_service)
):
    return await service.get_organizations_by_activity_deep(activity_id)


@router.get("/in_radius", response_model=list[OrganizationDetailRead])
async def organizations_in_radius(
        lat: float = Query(...),
        lng: float = Query(...),
        radius: float = Query(...),
        service: OrganizationService = Depends(get_organization_service)
):
    return await service.get_organizations_in_radius(lat, lng, radius)


@router.get("/in_rectangle", response_model=list[OrganizationDetailRead])
async def organizations_in_rectangle(
        min_lat: float = Query(...),
        max_lat: float = Query(...),
        min_lng: float = Query(...),
        max_lng: float = Query(...),
        service: OrganizationService = Depends(get_organization_service)
):
    return await service.get_organizations_in_rectangle(min_lat, max_lat, min_lng, max_lng)
