import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session
from app.models.user import User, UserStatus
from app.main import app
from app.core.deps import get_current_user_claims

@pytest.mark.asyncio
async def test_get_all_users_admin(client: AsyncClient, db_session: Session):
    # Setup: Explicitly create an admin user
    admin = User(
        full_name="Admin One",
        email="admin@example.com",
        clerk_id="admin_1",
        is_admin=True,
        status=UserStatus.APPROVED
    )
    db_session.add(admin)

    # Create another user
    user2 = User(
        full_name="User Two",
        email="user2@example.com",
        clerk_id="user_2",
        status=UserStatus.PENDING
    )
    db_session.add(user2)
    db_session.commit()

    # Override auth to use our admin
    app.dependency_overrides[get_current_user_claims] = lambda: {
        "sub": "admin_1",
        "email": "admin@example.com",
        "name": "Admin One"
    }

    # Test: Admin accesses /api/v1/admin/users
    response = await client.get("/api/v1/admin/users")
    assert response.status_code == 200
    data = response.json()

    # Should see exactly two users
    assert len(data) == 2
    emails = [u["email"] for u in data]
    assert "admin@example.com" in emails
    assert "user2@example.com" in emails

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_get_all_users_non_admin(client: AsyncClient, db_session: Session):
    # Setup: Create an admin first to ensure bootstrap logic is "used up"
    admin = User(
        full_name="Admin",
        email="admin@example.com",
        clerk_id="admin_clerk",
        is_admin=True,
        status=UserStatus.APPROVED
    )
    db_session.add(admin)

    # Create a non-admin user
    normal = User(
        full_name="Normal User",
        email="normal@example.com",
        clerk_id="user_normal",
        is_admin=False,
        status=UserStatus.APPROVED
    )
    db_session.add(normal)
    db_session.commit()

    # Mock auth as the normal user
    app.dependency_overrides[get_current_user_claims] = lambda: {
        "sub": "user_normal",
        "email": "normal@example.com"
    }

    # Test: Non-admin tries to access /api/v1/admin/users
    response = await client.get("/api/v1/admin/users")

    # Should get 403 Forbidden
    assert response.status_code == 403

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_revoke_user_flow(client: AsyncClient, db_session: Session):
    # Setup: Create an admin and an approved user
    admin = User(
        full_name="Admin",
        email="admin@example.com",
        clerk_id="admin_clerk",
        is_admin=True,
        status=UserStatus.APPROVED
    )
    db_session.add(admin)

    user_to_revoke = User(
        full_name="To Revoke",
        email="revoke@example.com",
        clerk_id="user_revoke",
        is_admin=False,
        status=UserStatus.APPROVED
    )
    db_session.add(user_to_revoke)
    db_session.commit()
    user_id = user_to_revoke.id

    # Mock auth as admin
    app.dependency_overrides[get_current_user_claims] = lambda: {
        "sub": "admin_clerk",
        "email": "admin@example.com"
    }

    # Test: Admin revokes user
    response = await client.post(f"/api/v1/admin/users/{user_id}/revoke")
    assert response.status_code == 200
    assert response.json()["status"] == UserStatus.REJECTED

    # Test: Revoked user tries to access a protected route
    app.dependency_overrides[get_current_user_claims] = lambda: {
        "sub": "user_revoke",
        "email": "revoke@example.com"
    }

    # Accessing personal profile might still work if get_current_user doesn't check status,
    # but get_authorized_user (used in router.py prefixes) should block it.
    # Parts is protected by get_authorized_user
    response = await client.get("/api/v1/parts")
    assert response.status_code == 403

    app.dependency_overrides.clear()
