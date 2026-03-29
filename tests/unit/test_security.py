import pytest
from unittest.mock import AsyncMock, patch
from jose import JWTError
from fastapi import HTTPException
from app.core import security
from app.core.config import settings
import time

@pytest.mark.asyncio
async def test_get_jwks_network_failure():
    # Force _get_jwks network fail by clearing cache first
    security._jwks_cache = None
    security._jwks_last_fetched = 0
    with patch("httpx.AsyncClient.get", side_effect=Exception("Network error")):
        with pytest.raises(HTTPException) as exc_info:
            await security._get_jwks()
        assert exc_info.value.status_code == 503
        assert "JWKS unavailable" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_get_jwks_ttl():
    with patch("app.core.security.time.time") as mock_time:
        from unittest.mock import MagicMock
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"keys": ["new"]}
            mock_get.return_value = mock_response

            # Reset cache
            security._jwks_cache = None
            security._jwks_last_fetched = 0

            # First fetch
            mock_time.return_value = 1000
            await security._get_jwks()
            assert mock_get.call_count == 1

            # Second fetch within TTL (3600s)
            mock_time.return_value = 1500
            await security._get_jwks()
            assert mock_get.call_count == 1

            # Third fetch after TTL
            mock_time.return_value = 5000
            await security._get_jwks()
            assert mock_get.call_count == 2

@pytest.mark.asyncio
async def test_verify_clerk_token_issuer_validation():
    with patch("app.core.security.settings") as mock_settings:
        mock_settings.CLERK_ISSUER_URL = "https://correct.com"
        mock_settings.CLERK_AUDIENCE = "aud"

        with patch("app.core.security._get_jwks", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"keys": []}
            with patch("jose.jwt.decode", side_effect=JWTError("Invalid issuer")):
                with pytest.raises(HTTPException) as exc:
                    await security.verify_clerk_token("token")
                assert exc.value.status_code == 401
                assert "Invalid" in exc.value.detail

@pytest.mark.asyncio
async def test_jwks_refresh_on_key_not_found():
    with patch("app.core.security._decode_and_verify", new_callable=AsyncMock) as mock_decode:
        mock_decode.side_effect = [
            JWTError("Key not found"),
            {"sub": "user_123"}
        ]
        with patch("app.core.security._get_jwks", new_callable=AsyncMock) as mock_get:
            result = await security.verify_clerk_token("token")
            assert result["sub"] == "user_123"
            mock_get.assert_called_with(force_refresh=True)
