import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_test_areas_crud(client: AsyncClient):
    # 1. Create TestArea
    create_payload = {"area": "reading", "part_id": None}
    response = await client.post("/api/v1/test-areas", json=create_payload)
    assert response.status_code == 201
    created_id = response.json()["area_id"]
    assert created_id is not None

    # 2. Get All Check
    response = await client.get("/api/v1/test-areas")
    assert response.status_code == 200
    assert len(response.json()) >= 1

    # 3. Get single
    response = await client.get(f"/api/v1/test-areas/{created_id}")
    assert response.status_code == 200
    assert response.json()["area_id"] == created_id

    # 4. Update
    update_payload = {"area": "writing", "part_id": None}
    response = await client.put(f"/api/v1/test-areas/{created_id}", json=update_payload)
    assert response.status_code == 200
    assert response.json()["area_name"] == "writing"

    # 5. Delete
    response = await client.delete(f"/api/v1/test-areas/{created_id}")
    assert response.status_code == 204

    # 6. Get single (should fail)
    response = await client.get(f"/api/v1/test-areas/{created_id}")
    assert response.status_code == 404
