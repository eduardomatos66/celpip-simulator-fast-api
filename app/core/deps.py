"""
FastAPI dependency injection utilities.
"""

from typing import Annotated, Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import verify_clerk_token
from app.models.user import User
from app.services import user_service

_bearer_scheme = HTTPBearer()


def get_db() -> Generator[Session, None, None]:
    """Yield a synchronous database session."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


from app.core.logger import logger

async def get_current_user_claims(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer_scheme)],
) -> dict:
    """
    Verify the Bearer token and return the decoded Clerk JWT claims.
    """
    try:
        claims = await verify_clerk_token(credentials.credentials)
        return claims
    except HTTPException:
        # Re-raise HTTPExceptions from verify_clerk_token (already logged there)
        raise
    except Exception as e:
        logger.error(f"Unexpected error during token verification: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials.",
        )


# Convenience aliases used in route signatures
CurrentUserClaims = Annotated[dict, Depends(get_current_user_claims)]
DBSession = Annotated[Session, Depends(get_db)]


async def get_current_user(
    claims: CurrentUserClaims,
    db: DBSession,
) -> User:
    """
    Fetch the User model from the database using the Clerk 'sub' claim.
    Creates the user if they don't exist yet (sync on first login).
    """
    clerk_id = claims.get("sub")
    
    # Try multiple common Clerk email claims to match what the webhook sends
    email = (
        claims.get("email") or 
        claims.get("primary_email_address") or 
        claims.get("email_address")
    )
    
    if not email:
        # Fallback to satisfy DB/Schema constraints if Clerk is misconfigured
        # Using @clerk.com because .local is a reserved TLD and fails Pydantic validation
        email = f"user_{clerk_id}@clerk.com"
        logger.warning(f"No email found in JWT claims for {clerk_id}. Using fallback: {email}. Claims: {claims.keys()}")

    # Extract name with multiple potential keys
    full_name = (
        claims.get("name") or 
        claims.get("full_name") or 
        claims.get("given_name", "") + " " + claims.get("family_name", "")
    ).strip() or "New User"
    
    user = user_service.get_or_create_user(db, clerk_id, email, full_name)
    return user


from app.models.user import User, UserStatus


async def get_authorized_user(
    user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Ensure the user is authorized by an admin.
    """
    if user.status != UserStatus.APPROVED:
        detail = "User not authorized by admin. Please contact support."
        if user.status == UserStatus.REJECTED:
            detail = "Your account request has been denied. Please contact support."
            
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )
    return user


async def get_admin_user(
    user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Ensure the user has admin privileges.
    """
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required.",
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
AuthorizedUser = Annotated[User, Depends(get_authorized_user)]
AdminUser = Annotated[User, Depends(get_admin_user)]

