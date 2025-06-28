from app.db.models import Building
from app.repositories.base import BaseRepository


class BuildingRepository(BaseRepository):
    model = Building
