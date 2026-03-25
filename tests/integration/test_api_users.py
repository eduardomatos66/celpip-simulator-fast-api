import pytest
from httpx import AsyncClient
from app.main import app
from app.core.deps import get_current_user_claims

def override_get_current_user_claims():
    return {"sub": "test_clerk_user_id", "email": "clerk_user@example.com"}

app.dependency_overrides[get_current_user_claims] = override_get_current_user_claims

@pytest.mark.asyncio
async def test_get_current_user_profile(client: AsyncClient):
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 200
    
    data = response.json()
    assert data["clerk_id"] == "test_clerk"
    assert data["email"] == "test@example.com"
