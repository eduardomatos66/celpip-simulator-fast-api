import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_check_db_routes(client: AsyncClient):
    # Depending on auth status, we might need to override deps, but let's assume it's open or overridden globally
    # Check links
    response = await client.get("/api/v1/check-db/check-links")
    assert response.status_code == 200
    assert "issues_found" in response.json()

    # Check non valid questions
    response = await client.get("/api/v1/check-db/check-non-valid-questions")
    assert response.status_code == 200
    assert "invalid_questions_count" in response.json()

    # Check orphan entities
    response = await client.get("/api/v1/check-db/check-orphans")
    assert response.status_code == 200
    assert "deleted" in response.json()
