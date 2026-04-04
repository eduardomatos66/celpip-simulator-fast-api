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
    # We allow a small mismatch in trailing slashes for issuer/audience
    # as this is a common Clerk config pitfall.
    issuer = settings.CLERK_ISSUER_URL.rstrip("/") if settings.CLERK_ISSUER_URL else None
    audience = settings.CLERK_AUDIENCE.rstrip("/") if settings.CLERK_AUDIENCE else None

    verify_options = {
        "verify_aud": bool(audience),
        "verify_iss": bool(issuer),
        "leeway": 300, # 5 minutes leeway (in seconds)
    }

    # Internal helper to try decoding with and without trailing slashes
    def _do_decode(jwk_or_key, iss, aud):
        return jwt.decode(
            token,
            jwk_or_key,
            algorithms=["RS256"],
            audience=aud,
            issuer=iss,
            options=verify_options,
        )

    try:
        # 1. Try Local PEM if available
        if settings.CLERK_JWT_KEY:
            try:
                # Try primary match
                return _do_decode(settings.CLERK_JWT_KEY, issuer, audience)
            except JWTError as e:
                if "Invalid issuer" in str(e) and issuer:
                    # Retry with trailing slash if configured without one
                    try:
                        return _do_decode(settings.CLERK_JWT_KEY, f"{issuer}/", audience)
                    except JWTError:
                        raise e
                if "Invalid audience" in str(e) and audience:
                    # Retry with trailing slash
                    try:
                        return _do_decode(settings.CLERK_JWT_KEY, issuer, f"{audience}/")
                    except JWTError:
                        raise e
                raise

        # 2. Fallback to JWKS verification
        jwks = await _get_jwks()
        try:
            return _do_decode(jwks, issuer, audience)
        except JWTError as e:
            if "Invalid issuer" in str(e) and issuer:
                 try:
                    return _do_decode(jwks, f"{issuer}/", audience)
                 except JWTError:
                    raise e
            if "Invalid audience" in str(e) and audience:
                 try:
                    return _do_decode(jwks, issuer, f"{audience}/")
                 except JWTError:
                    raise e
            raise
    except JWTError as e:
        # Debugging: Peek into the token without verification to see what's actually there
        try:
            unverified_claims = jwt.get_unverified_claims(token)
            logger.error(
                f"JWT verification failed: {e}. "
                f"Configured issuer: {issuer}, Configured audience: {audience}. "
                f"Token claims (unverified): {unverified_claims}"
            )
        except Exception:
            logger.error(f"JWT verification failed: {e}. Could not parse unverified claims.")
        raise


def _handle_auth_error(exc: Exception):
    error_msg = str(exc)
    # Be more descriptive for common Clerk issues
    if "Signature has expired" in error_msg:
        detail = "Your session has expired. Please log in again."
    elif "Invalid issuer" in error_msg:
        detail = f"Authentication configuration mismatch (Issuer). {error_msg}"
    elif "Invalid audience" in error_msg:
        detail = f"Authentication configuration mismatch (Audience). {error_msg}"
    elif "Key not found" in error_msg:
        detail = "Authentication key rotation error. Please try again in 1 minute."
    else:
        detail = f"Authentication failed: {error_msg}"

    logger.warning(f"Returning 401: {detail}. Check your .env CLERK_ISSUER_URL and CLERK_AUDIENCE.")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )
