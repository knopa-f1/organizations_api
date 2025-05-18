from typing import Any, Coroutine

from sqlalchemy import select, text
from sqlalchemy.orm import joinedload, selectinload

from app.api.schemas.organizations import OrganizationRead, OrganizationDetailRead
from app.db.models import Organization, Phone, organization_activities, Activity
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

    async def get_by_id(self, organization_id: int) -> OrganizationDetailRead | None:
        stmt = (
            select(Organization)
            .where(Organization.id == organization_id)
            .options(
                joinedload(Organization.phones),
                joinedload(Organization.activities),
            )
        )
        result = await self.session.execute(stmt)
        org = result.unique().scalar_one_or_none()
        if not org:
            return None
        else:
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
        else:
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

    async def get_by_activity_with_subtree(self, activity_id: int) -> list[Organization]:
        stmt = text("""
                    SELECT organization_id
                    FROM organization_activities
                    WHERE activity_id IN (
                        SELECT act.id
                        FROM activity AS act
                        WHERE act.id = :activity_id
                    
                        UNION ALL
                    
                        SELECT act_child.id
                        FROM activity AS act_child
                        WHERE act_child.parent_id = :activity_id
                    
                        UNION ALL
                    
                        SELECT act_child_child.id
                        FROM activity AS act_child
                        JOIN activity AS act_child_child ON act_child_child.parent_id = act_child.id
                        WHERE act_child.parent_id = :activity_id
                    )
                """)

        result = await self.session.execute(stmt, {"activity_id": activity_id})
        org_ids = result.scalars().all()

        if org_ids:
            stmt_details = (
                select(Organization)
                .options(
                    selectinload(Organization.phones),
                    selectinload(Organization.activities)
                )
                .where(Organization.id.in_(org_ids))
            )
            detailed_result = await self.session.execute(stmt_details)
            return detailed_result.scalars().all()
        return []
