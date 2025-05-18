from app.db.database import async_session_maker

from app.repositories.activities import ActivityRepository
from app.repositories.buildings import BuildingRepository
from app.repositories.organizations import OrganizationRepository


class UnitOfWork:
    def __init__(self, session_factory=None):
        if session_factory is None:
            self.session_factory = async_session_maker
        else:
            self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()
        self.buildings = BuildingRepository(self.session)
        self.organizations = OrganizationRepository(self.session)
        self.activities = ActivityRepository(self.session)
        return self

    async def __aexit__(self, *args):
        await self.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
