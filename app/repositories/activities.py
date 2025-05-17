from sqlalchemy import select
from app.db.models import Activity
from app.repositories.base import BaseRepository


class ActivityRepository(BaseRepository):
    model = Activity

    async def check_depth(self, activity_id: int, max_depth: int = 3):
        depth = 0
        current_id = activity_id

        while current_id is not None:
            depth += 1
            if depth > max_depth:
                raise ValueError(f"Уровень вложенности не может превышать {max_depth}")

            activity = await self.get_by_id(current_id)
            if not activity:
                break
            current_id = activity.parent_id
