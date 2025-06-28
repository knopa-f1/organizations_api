import pytest
from httpx import AsyncClient

from app.core.config import settings

API_KEY = settings.API_KEY


@pytest.mark.anyio
async def test_create_building(client: AsyncClient):
    response = await client.post(
        "/buildings/",
        json={"name": "Tech Park Tower",
              "address": "ул. Ленина, 1",
              "latitude": 54.6872,
              "longitude": 25.2797
              },
        headers={"X-API-Key": API_KEY}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["address"] == "ул. Ленина, 1"
    assert "id" in data


@pytest.mark.anyio
async def test_list_buildings(client: AsyncClient):
    response = await client.get("/buildings/", headers={"X-API-Key": API_KEY})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
