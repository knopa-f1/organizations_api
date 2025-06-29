from sqlalchemy import select
from sqlalchemy.orm import selectinload

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

    async def get_activity_subtree_ids(self, root_id: int, max_depth: int = 2) -> list[int]:
        stmt = select(Activity).where(Activity.id == root_id).options(selectinload(Activity.children))
        result = await self.session.execute(stmt)
        root = result.scalar_one_or_none()

        if root is None:
            return []

        collected = set()
        collected.add(root.id)

        async def collect_recursive(activity: Activity, level: int = 0):
            if level > max_depth:
                return
            for child in activity.children:
                collected.add(child.id)
                stmt = select(Activity).where(Activity.id == child.id).options(selectinload(Activity.children))
                result = await self.session.execute(stmt)
                child_full = result.scalar_one()
                await collect_recursive(child_full, level + 1)

        await collect_recursive(root)
        return list(collected)
