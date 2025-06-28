import pytest
from httpx import AsyncClient

from app.core.config import settings

API_KEY = settings.API_KEY


@pytest.mark.anyio
async def test_create_organization(client: AsyncClient):
    building = await client.post("/buildings/",
                                 json={"name": "Tech Park Tower",
                                       "address": "ул. Ленина, 1",
                                       "latitude": 54.6872,
                                       "longitude": 95.2797
                                       },
                                 headers={"X-API-Key": API_KEY})
    activity = await client.post("/activities/", json={"name": "IT", 'parent_id': None}, headers={"X-API-Key": API_KEY})

    building_id = building.json()["id"]
    activity_id = activity.json()["id"]

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

    r = await client.post("/activities/", json={"name": "Мясная продукция", "parent_id": food_id},
                          headers={"X-API-Key": API_KEY})
    meat_id = r.json()["id"]

    r = await client.post("/activities/", json={"name": "Молочная продукция", "parent_id": food_id},
                          headers={"X-API-Key": API_KEY})
    milk_id = r.json()["id"]

    r = await client.post("/buildings/",
                          json={"name": "Food Tower", "address": "ул. Вкусная, 10", "latitude": 54.0,
                                "longitude": 25.0},
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

@pytest.mark.anyio
async def test_organizations_in_radius(client: AsyncClient):
    building = await client.post("/buildings/", json={
        "name": "Central Office",
        "address": "Центр города",
        "latitude": 54.6872,
        "longitude": 25.2797
    }, headers={"X-API-Key": API_KEY})

    building_id = building.json()["id"]

    await client.post("/organizations/", json={
        "name": "Org в радиусе",
        "building_id": building_id,
        "phones": [],
        "activity_ids": []
    }, headers={"X-API-Key": API_KEY})

    response = await client.get("/organizations/in_radius", params={
        "lat": 54.6870,
        "lng": 25.2790,
        "radius": 1
    }, headers={"X-API-Key": API_KEY})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Org в радиусе"


@pytest.mark.anyio
async def test_organizations_in_rectangle(client: AsyncClient):
    building_1 = await client.post("/buildings/", json={
        "name": "Внутри прямоугольника",
        "address": "Пример 1",
        "latitude": 54.6850,
        "longitude": 25.2800
    }, headers={"X-API-Key": API_KEY})

    building_2 = await client.post("/buildings/", json={
        "name": "Снаружи прямоугольника",
        "address": "Пример 2",
        "latitude": 54.7000,
        "longitude": 25.3000
    }, headers={"X-API-Key": API_KEY})

    inside_id = building_1.json()["id"]
    outside_id = building_2.json()["id"]

    await client.post("/organizations/", json={
        "name": "Org Внутри",
        "building_id": inside_id,
        "phones": [],
        "activity_ids": []
    }, headers={"X-API-Key": API_KEY})

    await client.post("/organizations/", json={
        "name": "Org Снаружи",
        "building_id": outside_id,
        "phones": [],
        "activity_ids": []
    }, headers={"X-API-Key": API_KEY})

    response = await client.get("/organizations/in_rectangle", params={
        "min_lat": 54.6800,
        "max_lat": 54.6900,
        "min_lng": 25.2700,
        "max_lng": 25.2900
    }, headers={"X-API-Key": API_KEY})

    assert response.status_code == 200
    data = response.json()
    names = [org["name"] for org in data]
    assert "Org Внутри" in names
    assert "Org Снаружи" not in names
