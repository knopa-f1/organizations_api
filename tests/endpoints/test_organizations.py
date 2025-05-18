import pytest
from httpx import AsyncClient
from app.core.config import settings

API_KEY = settings.API_KEY


@pytest.mark.anyio
async def test_create_organization(client: AsyncClient):
    await client.post("/buildings/",
                      json={"name": "Tech Park Tower",
                              "address": "ул. Ленина, 1",
                              "latitude": 54.6872,
                              "longitude": 25.2797
                      },
                      headers={"X-API-Key": API_KEY})
    await client.post("/activities/", json={"name": "IT", 'parent_id':None}, headers={"X-API-Key": API_KEY})

    buildings = await client.get("/buildings/", headers={"X-API-Key": API_KEY})
    activities = await client.get("/activities/", headers={"X-API-Key": API_KEY})
    building_id = buildings.json()[0]["id"]
    activity_id = activities.json()[0]["id"]

    response = await client.post(
        "/organizations/",
        json={
            "name": "ТестОрг",
            "building_id": building_id,
            "phones": ["+123456"],
            "activity_ids": [activity_id]
        },
        headers={"X-API-Key": API_KEY}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "ТестОрг"
    assert "id" in data


@pytest.mark.anyio
async def test_search_organization_by_id(client: AsyncClient):
    all_orgs = await client.get("/organizations/list/", headers={"X-API-Key": API_KEY})
    assert len(all_orgs.json()) == 1
    org_id = all_orgs.json()[0]["id"]

    response = await client.get(f"/organizations/search?id={org_id}", headers={"X-API-Key": API_KEY})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == org_id
    assert data["name"] == "ТестОрг"


@pytest.mark.anyio
async def test_search_organization_by_name(client: AsyncClient):
    response = await client.get("/organizations/search?name=ТестОрг", headers={"X-API-Key": API_KEY})
    assert response.status_code == 200

@pytest.mark.anyio
async def test_orgs_by_activity_deep(client: AsyncClient):
    r = await client.post("/activities/", json={"name": "Еда", "parent_id": None}, headers={"X-API-Key": API_KEY})
    food_id = r.json()["id"]

    r = await client.post("/activities/", json={"name": "Мясная продукция", "parent_id": food_id}, headers={"X-API-Key": API_KEY})
    meat_id = r.json()["id"]

    r = await client.post("/activities/", json={"name": "Молочная продукция", "parent_id": food_id}, headers={"X-API-Key": API_KEY})
    milk_id = r.json()["id"]

    r = await client.post("/buildings/",
                          json={"name": "Food Tower", "address": "ул. Вкусная, 10", "latitude": 54.0, "longitude": 25.0},
                          headers={"X-API-Key": API_KEY})
    building_id = r.json()["id"]

    for name, activity_id in [("МяснаяОрг", meat_id), ("МолочнаяОрг", milk_id), ("ПростоЕда", food_id)]:
        await client.post("/organizations/",
                          json={
                              "name": name,
                              "building_id": building_id,
                              "phones": ["+123456789"],
                              "activity_ids": [activity_id]
                          },
                          headers={"X-API-Key": API_KEY})

    r = await client.get(f"/organizations/by_activity/{food_id}", headers={"X-API-Key": API_KEY})
    assert r.status_code == 200
    names = {org["name"] for org in r.json()}
    assert names == {"МяснаяОрг", "МолочнаяОрг", "ПростоЕда"}
