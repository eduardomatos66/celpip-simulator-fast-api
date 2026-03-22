"""
Clerk JWT verification utilities.

Fetches the JWKS from Clerk's public endpoint and validates incoming Bearer tokens.
"""

import httpx
from jose import jwt, JWTError
from fastapi import HTTPException, status

from app.core.config import settings

_jwks_cache: dict | None = None


async def _get_jwks() -> dict:
    """Fetch and cache Clerk's JSON Web Key Set."""
    global _jwks_cache
    if _jwks_cache is None:
        async with httpx.AsyncClient() as client:
            response = await client.get(settings.CLERK_JWKS_URL)
            response.raise_for_status()
            _jwks_cache = response.json()
    return _jwks_cache


async def verify_clerk_token(token: str) -> dict:
    """
    Verify a Clerk-issued JWT.

    Args:
        token: Raw Bearer token string.

    Returns:
        Decoded JWT claims dict (includes 'sub', 'email', etc.).

    Raises:
        HTTPException 401 if the token is invalid or expired.
    """
    try:
        jwks = await _get_jwks()
        claims = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            audience=settings.CLERK_AUDIENCE or None,
            options={"verify_aud": bool(settings.CLERK_AUDIENCE)},
        )
        return claims
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        )
