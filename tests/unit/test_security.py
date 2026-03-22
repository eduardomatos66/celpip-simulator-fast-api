import pytest
from unittest.mock import patch
from fastapi import HTTPException
from app.core.security import verify_clerk_token
from app.core.config import settings

@pytest.mark.asyncio
@patch("app.core.security._get_jwks")
async def test_verify_clerk_token_invalid_format(mock_get_jwks):
    settings.CLERK_JWKS_URL = "https://fake.clerk.dev/.well-known/jwks.json"
    settings.CLERK_AUDIENCE = "https://fake"
    
    mock_get_jwks.return_value = {"keys": []}
    
    # If a totally garbage token is bypassed, python-jose throws or returns empty
    with pytest.raises(HTTPException) as exc:
        await verify_clerk_token("invalid.token.here")
    assert exc.value.status_code == 401
    mock_get_jwks.assert_called_once()

@pytest.mark.asyncio
@patch("app.core.security._get_jwks")
async def test_verify_clerk_token_fetches_jwks(mock_get_jwks):
    settings.CLERK_JWKS_URL = "https://fake.clerk.dev/.well-known/jwks.json"
    settings.CLERK_AUDIENCE = "https://fake"
    
    mock_get_jwks.return_value = {"keys": []}
    
    # Verify that python-jose throws verification error because the token signature 
    # won't match the mocked empty keys list
    valid_format_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6InRlc3QifQ.e30.c2ln"
    with pytest.raises(HTTPException) as exc:
        await verify_clerk_token(valid_format_token)
        
    assert exc.value.status_code == 401
    mock_get_jwks.assert_called_once()
