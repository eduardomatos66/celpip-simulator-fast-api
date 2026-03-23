import pytest
from unittest.mock import patch, MagicMock
from app.core import security
from fastapi import HTTPException

@pytest.mark.asyncio
async def test_get_jwks_network_failure():
    # Force _get_jwks network fail by clearing cache first
    security._jwks_cache = None
    with patch("httpx.AsyncClient.get", side_effect=Exception("Network error")):
        with pytest.raises(Exception) as exc_info:
            await security._get_jwks()
        assert "Network error" in str(exc_info.value)

@pytest.mark.asyncio
async def test_verify_clerk_token_invalid_format():
    with patch("app.core.security._get_jwks", return_value={"keys": []}):
        with pytest.raises(HTTPException) as exc:
            await security.verify_clerk_token("invalid_token")
        assert exc.value.status_code == 401
        assert "Invalid or expired token" in str(exc.value.detail)
