from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import CurrentUser
from app.schemas.user import UserRead

router = APIRouter()

@router.get("/me", response_model=UserRead)
def get_current_user_profile(user: CurrentUser):
    """
    Get the current user's profile.
    This also behaves as a login sync endpoint, creating the local User DB record
    if this is the first time the user logs in through Clerk.
    """
    return user
