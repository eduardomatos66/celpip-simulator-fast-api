import pytest
from httpx import AsyncClient
from app.main import app
from app.core.deps import get_current_user_claims

# Override auth dependency
def override_get_current_user_claims():
    return {"sub": "test_clerk_id", "email": "clerk@example.com"}

app.dependency_overrides[get_current_user_claims] = override_get_current_user_claims


@pytest.mark.asyncio
async def test_submit_answer_sheet(client: AsyncClient):
    payload = {
        "test_id": 999,
        "mode": "practice",
        "option_answers": [
            {"option_id": 1, "is_correct": True}
        ]
    }
    response = await client.post("/api/v1/answer-sheets", json=payload)
    
    # Can return 404 missing user or test, but endpoint logic must be hit
    # With a fresh memory DB we expect the code to reach internal logic safely
    assert response.status_code in [200, 404, 400]

@pytest.mark.asyncio
async def test_get_answer_sheet(client: AsyncClient):
    response = await client.get("/api/v1/answer-sheets/99999")
    # Will likely return 404
    assert response.status_code == 404
