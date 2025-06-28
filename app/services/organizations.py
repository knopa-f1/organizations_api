from math import radians, cos

from fastapi import HTTPException

from app.api.schemas.organizations import OrganizationCreate, OrganizationRead, OrganizationDetailRead
from app.utils.unitofwork import UnitOfWork


class OrganizationService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def add_organization(self, data: OrganizationCreate) -> OrganizationRead:
        async with self.uow:
            data_dict = data.model_dump()
            organization = await self.uow.organizations.create(data_dict['name'],
                                                               data_dict['building_id'],
                                                               data_dict['phones'],
                                                               data_dict['activity_ids'])
            await self.uow.commit()
            return organization

    async def get_organizations_by_activity_deep(self, activity_id: int):
        async with self.uow:
            activity_ids = await self.uow.activities.get_activity_subtree_ids(activity_id)
            orgs = await self.uow.organizations.get_by_activity_with_subtree(activity_ids)
            return [org.to_pydantic_model() for org in orgs]

    async def get_filtered_organizations(self, building_id: int | None = None, activity_id: int | None = None):
        async with self.uow:
            orgs = await self.uow.organizations.get_filtered(building_id, activity_id)
            return [org.to_pydantic_model() for org in orgs]

    async def get_by_id(self, organization_id: int) -> OrganizationDetailRead:
        async with self.uow:
            org = await self.uow.organizations.get_by_id(organization_id)
            if not org:
                raise HTTPException(status_code=404, detail=f"Не удалось найти организацию с id = {organization_id}")
            return org

    async def get_by_name(self, name: str) -> OrganizationDetailRead:
        async with self.uow:
            org = await self.uow.organizations.get_by_name(name)
            if not org:
                raise HTTPException(status_code=404, detail=f"Не удалось найти организацию с name = {name}")
            return org

    async def get_organizations_in_radius(self, center_lat: float, center_lng: float, radius_km: float):
        lat_km = 111.0
        lng_km = 111.0 * cos(radians(center_lat))

        delta_lat = radius_km / lat_km
        delta_lng = radius_km / lng_km

        min_lat = center_lat - delta_lat
        max_lat = center_lat + delta_lat
        min_lng = center_lng - delta_lng
        max_lng = center_lng + delta_lng
        async with self.uow:
            orgs = await self.uow.organizations.get_in_area(min_lat, max_lat, min_lng, max_lng)
            return [org.to_pydantic_model() for org in orgs]

    async def get_organizations_in_rectangle(self, min_lat: float, max_lat: float, min_lng: float, max_lng: float):
        async with self.uow:
            orgs = await self.uow.organizations.get_in_area(min_lat, max_lat, min_lng, max_lng)
            return [org.to_pydantic_model() for org in orgs]
