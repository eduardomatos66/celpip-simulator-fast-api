"""
FastAPI dependency injection utilities.
"""

from typing import Annotated, Generator

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import verify_clerk_token

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


async def get_current_user_claims(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer_scheme)],
) -> dict:
    """
    Verify the Bearer token and return the decoded Clerk JWT claims.

    Raises:
        HTTPException 401: If the token is missing or invalid.
    """
    return await verify_clerk_token(credentials.credentials)


# Convenience aliases used in route signatures
CurrentUserClaims = Annotated[dict, Depends(get_current_user_claims)]
DBSession = Annotated[Session, Depends(get_db)]

