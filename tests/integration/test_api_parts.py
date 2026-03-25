import pytest
from httpx import AsyncClient
from app.models.quiz import Part

@pytest.mark.asyncio
async def test_get_parts(client: AsyncClient, db_session):
    part = Part(part_number=1, part_name="Test Part")
    db_session.add(part)
    db_session.commit()

    response = await client.get("/api/v1/parts")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

@pytest.mark.asyncio
async def test_get_part_by_id(client: AsyncClient, db_session):
    part = Part(part_number=2, part_name="Get By ID")
    db_session.add(part)
    db_session.commit()

    response = await client.get(f"/api/v1/parts/{part.part_id}")
    assert response.status_code == 200
    assert response.json()["part_name"] == "Get By ID"

@pytest.mark.asyncio
async def test_get_sections_for_part(client: AsyncClient, db_session):
    part = Part(part_number=3, part_name="With Sections")
    db_session.add(part)
    db_session.commit()

    response = await client.get(f"/api/v1/parts/{part.part_id}/sections")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_get_part_not_found(client: AsyncClient):
    response = await client.get("/api/v1/parts/999999")
    assert response.status_code == 404
