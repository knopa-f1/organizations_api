from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from app.api.schemas.organizations import OrganizationRead, OrganizationDetailRead
from app.db.models import Organization, Phone, organization_activities, Activity, Building
from app.repositories.base import BaseRepository


class OrganizationRepository(BaseRepository):
    model = Organization

    async def create(
            self,
            name: str,
            building_id: int,
            phones: list[str],
            activity_ids: list[int],
    ) -> OrganizationRead:

        org = Organization(name=name, building_id=building_id)
        self.session.add(org)
        await self.session.flush()

        self.session.add_all(
            [Phone(number=phone, organization_id=org.id) for phone in phones]
        )

        await self.session.execute(
            organization_activities.insert().values([
                {"organization_id": org.id, "activity_id": activity_id}
                for activity_id in activity_ids
            ])
        )

        await self.session.flush()
        org = (
            await self.session.execute(
                select(Organization)
                .options(
                    selectinload(Organization.phones),
                    selectinload(Organization.activities),
                )
                .where(Organization.id == org.id)
            )
        ).scalar_one()
        return org.to_pydantic_model()

    async def get_by_id(self, obj_id: int) -> OrganizationDetailRead | None:
        stmt = (
            select(Organization)
            .where(Organization.id == obj_id)
            .options(
                joinedload(Organization.phones),
                joinedload(Organization.activities),
            )
        )
        result = await self.session.execute(stmt)
        org = result.unique().scalar_one_or_none()
        if not org:
            return None
        return org.to_pydantic_model()

    async def get_by_name(self, name: str) -> OrganizationDetailRead | None:
        stmt = (
            select(Organization)
            .where(Organization.name.ilike(f"%{name}%"))
            .options(
                joinedload(Organization.phones),
                joinedload(Organization.activities),
            )
        )
        result = await self.session.execute(stmt)
        org = result.unique().scalar_one_or_none()
        if not org:
            return None
        return org.to_pydantic_model()

    async def get_filtered(self, building_id: int | None = None, activity_id: int | None = None):
        stmt = select(Organization).distinct()

        if building_id:
            stmt = stmt.where(Organization.building_id == building_id)

        if activity_id:
            stmt = stmt.join(Organization.activities).where(Activity.id == activity_id)

        stmt = stmt.options(joinedload(Organization.phones), joinedload(Organization.activities))

        result = await self.session.execute(stmt)
        return result.unique().scalars().all()

    async def get_by_activity_with_subtree(self, activity_ids: list[int]) -> list[Organization]:
        stmt = (
            select(Organization)
            .join(Organization.activities)
            .options(
                selectinload(Organization.phones),
                selectinload(Organization.activities),
            )
            .where(Activity.id.in_(activity_ids))
            .distinct()
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_in_area(self, min_lat: float, max_lat: float, min_lng: float, max_lng: float):
        query = (
            select(Organization)
            .options(
                selectinload(Organization.phones),
                selectinload(Organization.activities),
            )
            .join(Organization.building)
            .where(
                Building.latitude.between(min_lat, max_lat),
                Building.longitude.between(min_lng, max_lng)
            )
        )
        result = await self.session.execute(query)
        return result.scalars().unique().all()
