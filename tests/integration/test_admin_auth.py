import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session
from app.models.user import User, UserStatus


@pytest.mark.asyncio
async def test_admin_authorization_flow(client: AsyncClient, db_session: Session):
    # 1. First user should be auto-authorized as admin (bootstrapping)
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["is_admin"] is True
    assert data["status"] == UserStatus.APPROVED
    admin_id = data["id"]

    # 2. Create another user (not authorized)
    from app.main import app
    from app.core.deps import get_current_user_claims

    app.dependency_overrides[get_current_user_claims] = lambda: {"sub": "user_2", "email": "user2@example.com", "name": "User Two"}

    response = await client.get("/api/v1/users/me")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "user2@example.com"
    assert data["is_admin"] is False
    assert data["status"] == UserStatus.PENDING
    user2_id = data["id"]

    # 3. New user tries to access protected endpoint
    response = await client.get("/api/v1/test-results/user")
    assert response.status_code == 403
    assert "not authorized" in response.json()["error"]["message"].lower()

    # 4. Admin (user 1) authorizes user 2
    app.dependency_overrides[get_current_user_claims] = lambda: {"sub": "test_clerk", "email": "test@example.com"}

    # List pending users
    response = await client.get("/api/v1/admin/users/pending")
    assert response.status_code == 200
    pending = response.json()
    assert any(u["id"] == user2_id for u in pending)

    # Authorize user 2
    response = await client.post(f"/api/v1/admin/users/{user2_id}/authorize")
    assert response.status_code == 200
    assert response.json()["status"] == UserStatus.APPROVED

    # 5. User 2 tries to access protected endpoint again
    app.dependency_overrides[get_current_user_claims] = lambda: {"sub": "user_2", "email": "user2@example.com", "name": "User Two"}

    response = await client.get("/api/v1/test-results/user")
    assert response.status_code != 403

    # 6. Test Rejection
    # Reset user 2 to pending for testing rejection (manual DB update for test)
    user2 = db_session.get(User, user2_id)
    user2.status = UserStatus.PENDING
    db_session.commit()

    # Admin rejects user 2
    app.dependency_overrides[get_current_user_claims] = lambda: {"sub": "test_clerk", "email": "test@example.com"}
    response = await client.post(f"/api/v1/admin/users/{user2_id}/reject")
    assert response.status_code == 200
    assert response.json()["status"] == UserStatus.REJECTED

    # User 2 tries to access protected endpoint and gets rejected message
    app.dependency_overrides[get_current_user_claims] = lambda: {"sub": "user_2", "email": "user2@example.com", "name": "User Two"}
    response = await client.get("/api/v1/test-results/user")
    assert response.status_code == 403
    assert "denied" in response.json()["error"]["message"].lower()

    app.dependency_overrides.clear()
