import pytest
from httpx import AsyncClient
from app.models.quiz import Section

@pytest.mark.asyncio
async def test_get_section_by_id(client: AsyncClient, db_session):
    section = Section(section_number=1, text="Section Get Test")
    db_session.add(section)
    db_session.commit()

    response = await client.get(f"/api/v1/sections/{section.section_id}")
    assert response.status_code == 200
    assert response.json()["text"] == "Section Get Test"

@pytest.mark.asyncio
async def test_get_section_not_found(client: AsyncClient):
    response = await client.get("/api/v1/sections/999999")
    assert response.status_code == 404
