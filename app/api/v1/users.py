from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import CurrentUser, get_db
from app.schemas.user import UserRead
from app.models.user import User

router = APIRouter()

@router.get("",
    response_model=List[UserRead],
    summary="List All Registered Users",
    description="Retrieve a list of all user profiles registered in the system. Mainly used for administrative overview.")
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.get("/me",
    response_model=UserRead,
    summary="Get My Profile",
    description="Retrieve the authenticated user's profile details. This endpoint also ensures the local database record exists, creating it if necessary (JIT provisioning).")
async def get_current_user_profile(user: CurrentUser):
    return user
