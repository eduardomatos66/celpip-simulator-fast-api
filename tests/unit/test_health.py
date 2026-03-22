"""
Phase 1 — Scaffolding smoke test.

Verifies the app starts and the health endpoint is reachable.
"""

import pytest


@pytest.mark.asyncio
async def test_health_endpoint(client):
    """GET /health should return 200 with status ok."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
