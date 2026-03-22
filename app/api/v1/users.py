from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import get_db, CurrentUserClaims
from app.schemas.user import UserRead
from app.services import user_service

router = APIRouter()

@router.get("/me", response_model=UserRead)
def get_current_user_profile(claims: CurrentUserClaims, db: Session = Depends(get_db)):
    """
    Get the current user's profile.
    This also behaves as a login sync endpoint, creating the local User DB record
    if this is the first time the user logs in through Clerk.
    """
    clerk_id = claims.get("sub")
    email = claims.get("email", "") 
    name = claims.get("name", "")
    
    # We may need to get email/name from Clerk token if they are mapped there
    user = user_service.get_or_create_user(db, clerk_id, email, name)
    return user
