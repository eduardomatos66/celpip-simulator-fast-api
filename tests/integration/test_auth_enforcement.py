import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_public_routes_accessible_without_auth(unauth_client: AsyncClient):
    """Verify that public routes are accessible without a token."""
    # /api/v1/test-available should be public
    response = await unauth_client.get("/api/v1/test-available")
    assert response.status_code == 200

    # /api/v1/users should be public
    response = await unauth_client.get("/api/v1/users")
    assert response.status_code == 200

    # /health should be public
    response = await unauth_client.get("/health")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_protected_routes_inaccessible_without_auth(unauth_client: AsyncClient):
    """Verify that protected routes return 403/401 without a token."""
    # /api/v1/tests is gone (404)
    response = await unauth_client.get("/api/v1/tests")
    assert response.status_code == 404

    # /api/v1/parts should be protected
    response = await unauth_client.get("/api/v1/parts")
    assert response.status_code in [401, 403]

    # /api/v1/test-available/1 should be protected (full detail)
    # Even if prefixed by public-ish name, we added the dependency internally
    response = await unauth_client.get("/api/v1/test-available/1")
    assert response.status_code in [401, 403]

@pytest.mark.asyncio
async def test_users_me_protected_internally(unauth_client: AsyncClient):
    """Verify that /users/me is protected even if /users is not."""
    response = await unauth_client.get("/api/v1/users/me")
    assert response.status_code in [401, 403]
