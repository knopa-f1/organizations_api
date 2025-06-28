import pytest
from httpx import AsyncClient

from app.core.config import settings

API_KEY = settings.API_KEY


@pytest.mark.anyio
async def test_create_activity(client: AsyncClient):
    response = await client.post(
        "/activities/",
        json={"name": "Еда", "parent_id": None},
        headers={"X-API-Key": API_KEY}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Еда"
    assert data["id"] is not None


@pytest.mark.anyio
async def test_list_activities(client: AsyncClient):
    response = await client.get("/activities/", headers={"X-API-Key": API_KEY})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
