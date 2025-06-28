from fastapi import HTTPException, status

from app.api.schemas.activities import ActivityCreate, ActivityRead
from app.utils.unitofwork import UnitOfWork


class ActivityService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def add_activity(self, data: ActivityCreate) -> ActivityRead:
        async with self.uow:
            try:
                if data.parent_id is not None:
                    await self.uow.activities.check_depth(data.parent_id)

                activity = await self.uow.activities.add_one(data.model_dump())
                await self.uow.commit()
                return activity
            except ValueError as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def get_all_activities(self) -> list[ActivityRead]:
        async with self.uow:
            activities = await self.uow.activities.get_all()
            return [ActivityRead.model_validate(a) for a in activities]
