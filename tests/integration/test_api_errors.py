import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
from sqlalchemy.exc import IntegrityError
from app.main import app

@pytest.mark.asyncio
async def test_404_not_found(client: AsyncClient):
    """Test standard 404 from an unknown route."""
    response = await client.get("/api/v1/some-route-that-doesnt-exist")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["status"] == 404
    assert data["error"]["type"] == "HTTP Error"

@pytest.mark.asyncio
async def test_422_validation_error(client: AsyncClient):
    """Test 422 error thrown when a payload is totally omitted/invalid for POST."""
    response = await client.post("/api/v1/test-areas", json={"missing": "fields"})
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"]["status"] == 422
    assert data["error"]["type"] == "Validation Error"
    assert isinstance(data["error"]["details"], list)

@pytest.mark.asyncio
async def test_409_integrity_error(client: AsyncClient):
    """Test mapping an IntegrityError to a 409 Conflict."""
    with patch("app.services.test_area_service.get_test_areas") as mock_get:
        mock_get.side_effect = IntegrityError(None, None, Exception("Simulation"))
        response = await client.get("/api/v1/test-areas")

    assert response.status_code == 409
    data = response.json()
    assert "error" in data
    assert data["error"]["status"] == 409
    assert data["error"]["type"] == "Conflict"

@pytest.mark.asyncio
async def test_500_internal_error():
    """Test a raw unhandled exception is muffled safely."""
    from httpx import ASGITransport
    from app.core.deps import get_db, get_current_user_claims

    # We must bridge to the TestingSessionLocal to isolate this test's DB
    # and provide a mock user so it passes the AuthorizedUser check.
    from tests.conftest import TestingSessionLocal
    app.dependency_overrides[get_db] = lambda: TestingSessionLocal()
    app.dependency_overrides[get_current_user_claims] = lambda: {"sub": "test_clerk", "email": "test@example.com"}

    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as safe_client:
        with patch("app.services.test_area_service.get_test_areas") as mock_get:
            mock_get.side_effect = Exception("System Crash!")
            response = await safe_client.get("/api/v1/test-areas")

        assert response.status_code == 500
        data = response.json()
        assert "error" in data
        assert data["error"]["status"] == 500
        assert data["error"]["type"] == "Internal Server Error"
        assert "Crash!" not in data["error"]["message"]  # Stack trace protected

    app.dependency_overrides.clear()
