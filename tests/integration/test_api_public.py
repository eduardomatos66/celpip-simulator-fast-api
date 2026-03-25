import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_public_tests(unauth_client: AsyncClient):
    response = await unauth_client.get("/api/v1/tests")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_get_public_parts(unauth_client: AsyncClient):
    response = await unauth_client.get("/api/v1/parts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_protected_answer_sheets_requires_auth(unauth_client: AsyncClient):
    # no headers -> expects 403 / 401
    response = await unauth_client.get("/api/v1/answer-sheets/1")
    assert response.status_code in [401, 403]
