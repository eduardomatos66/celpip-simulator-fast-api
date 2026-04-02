from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import CurrentUser, get_db
from app.schemas.user import UserRead
from app.models.user import User

router = APIRouter()

@router.get("", response_model=List[str])
def list_users(db: Session = Depends(get_db)):
    """
    Compatibility: List all users (emails only).
    The frontend fetchUsers expects a string array.
    """
    return [u.email for u in db.query(User).all()]

@router.get("/me", response_model=UserRead)
async def get_current_user_profile(user: CurrentUser):
    """
    Get the current user's profile.
    This also behaves as a login sync endpoint, creating the local User DB record
    if this is the first time the user logs in through Clerk.
    """
    return user
