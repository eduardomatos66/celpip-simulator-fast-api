import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session
from app.models.user import User
from app.services import user_service

@pytest.mark.asyncio
async def test_admin_authorization_flow(client: AsyncClient, db_session: Session):
    # 1. First user should be auto-authorized as admin (bootstrapping)
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["is_admin"] is True
    assert data["is_authorized"] is True
    admin_id = data["id"]

    # 2. Create another user (not authorized)
    # We override the dependency for the next request to simulate another user
    from app.main import app
    from app.core.deps import get_current_user_claims
    
    app.dependency_overrides[get_current_user_claims] = lambda: {"sub": "user_2", "email": "user2@example.com", "name": "User Two"}
    
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "user2@example.com"
    assert data["is_admin"] is False
    assert data["is_authorized"] is False
    user2_id = data["id"]

    # 3. New user tries to access protected endpoint
    response = await client.get("/api/v1/test-results/user")
    assert response.status_code == 403
    assert "not authorized" in response.json()["error"]["message"].lower()

    # 4. Admin (user 1) authorizes user 2
    # Switch back to admin
    app.dependency_overrides[get_current_user_claims] = lambda: {"sub": "test_clerk", "email": "test@example.com"}
    
    # List pending users
    response = await client.get("/api/v1/admin/users/pending")
    assert response.status_code == 200
    pending = response.json()
    assert any(u["id"] == user2_id for u in pending)

    # Authorize user 2
    response = await client.post(f"/api/v1/admin/users/{user2_id}/authorize")
    assert response.status_code == 200
    assert response.json()["is_authorized"] is True

    # 5. User 2 tries to access protected endpoint again
    app.dependency_overrides[get_current_user_claims] = lambda: {"sub": "user_2", "email": "user2@example.com", "name": "User Two"}
    
    response = await client.get("/api/v1/test-results/user")
    # It might be 500 or 404 if no tests exist, but NOT 403
    assert response.status_code != 403
    
    app.dependency_overrides.clear()
