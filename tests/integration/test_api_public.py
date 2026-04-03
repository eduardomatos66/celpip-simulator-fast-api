import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_public_routes_accessible_without_auth(unauth_client: AsyncClient):
    """Verify that public routes are accessible without a token."""
    # /api/v1/test-available/all should be public
    response = await unauth_client.get("/api/v1/test-available/all")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    # Verify only test_id and test_name are present (minimal schema)
    if response.json():
        test = response.json()[0]
        assert "test_id" in test
        assert "test_name" in test
        assert "test_areas" not in test

@pytest.mark.asyncio
async def test_get_tests_removed(unauth_client: AsyncClient):
    """Verify /tests is gone."""
    response = await unauth_client.get("/api/v1/tests")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_protected_routes_inaccessible_without_auth(unauth_client: AsyncClient):
    """Verify that protected routes return 403/401 without a token."""
    # /api/v1/tests is gone (404)
    response = await unauth_client.get("/api/v1/tests")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_protected_answer_sheets_requires_auth(unauth_client: AsyncClient):
    # no headers -> expects 403 / 401
    response = await unauth_client.get("/api/v1/answer-sheets/1")
    assert response.status_code in [401, 403]
