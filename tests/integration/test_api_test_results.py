import pytest
from httpx import AsyncClient
from app.main import app
from app.core.deps import get_current_user_claims

def override_get_current_user_claims():
    return {"sub": "test_clerk_id", "email": "clerk@example.com"}

app.dependency_overrides[get_current_user_claims] = override_get_current_user_claims

from app.services.user_service import get_or_create_user

@pytest.mark.asyncio
async def test_get_user_results(client: AsyncClient, db_session):
    # Tests require the clerk user to actually exist in the DB
    user = get_or_create_user(db_session, "test_clerk", "test@example.com", "Test User")

    response = await client.get("/api/v1/test-results/user")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_delete_test_result(client: AsyncClient):
    response = await client.delete("/api/v1/test-results/99999")
    # Will likely return 404 because ID 99999 doesn't exist
    assert response.status_code == 404
