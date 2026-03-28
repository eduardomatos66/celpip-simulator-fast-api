"""
Clerk JWT verification utilities.

Fetches the JWKS from Clerk's public endpoint and validates incoming Bearer tokens.
"""

import time
import httpx
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.logger import logger

_jwks_cache: Optional[Dict[str, Any]] = None
_jwks_last_fetched: float = 0
JWKS_TTL = 3600  # 1 hour


async def _get_jwks(force_refresh: bool = False) -> Dict[str, Any]:
    """Fetch and cache Clerk's JSON Web Key Set with TTL."""
    global _jwks_cache, _jwks_last_fetched
    
    current_time = time.time()
    if force_refresh or _jwks_cache is None or (current_time - _jwks_last_fetched > JWKS_TTL):
        logger.info("Fetching fresh JWKS from Clerk...")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(settings.CLERK_JWKS_URL)
                response.raise_for_status()
                _jwks_cache = response.json()
                _jwks_last_fetched = current_time
            except Exception as e:
                logger.error(f"Failed to fetch JWKS: {e}")
                if _jwks_cache is None:
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Could not verify authentication tokens (JWKS unavailable)."
                    )
    return _jwks_cache


async def verify_clerk_token(token: str) -> Dict[str, Any]:
    """
    Verify a Clerk-issued JWT with issuer and audience validation.
    Handles JWKS rotation by retrying once on key-not-found errors.
    """
    try:
        return await _decode_and_verify(token)
    except JWTError as exc:
        # If verification fails, it might be due to a rotated key.
        # Try refreshing the JWKS once and re-verifying.
        if "Key not found" in str(exc) or "Invalid key" in str(exc):
            logger.warning("JWT verification failed (possible key rotation). Retrying with fresh JWKS...")
            try:
                await _get_jwks(force_refresh=True)
                return await _decode_and_verify(token)
            except JWTError as retry_exc:
                _handle_auth_error(retry_exc)
        _handle_auth_error(exc)


async def _decode_and_verify(token: str) -> Dict[str, Any]:
    jwks = await _get_jwks()
    return jwt.decode(
        token,
        jwks,
        algorithms=["RS256"],
        audience=settings.CLERK_AUDIENCE or None,
        issuer=settings.CLERK_ISSUER_URL or None,
        options={
            "verify_aud": bool(settings.CLERK_AUDIENCE),
            "verify_iss": bool(settings.CLERK_ISSUER_URL),
        },
    )


def _handle_auth_error(exc: Exception):
    logger.warning(f"Authentication failed: {exc}")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token.",
        headers={"WWW-Authenticate": "Bearer"},
    )
