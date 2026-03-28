from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.deps import DBSession, AdminUser
from app.schemas.user import UserRead, UserUpdate
from app.services import user_service

router = APIRouter()

@router.get("/users/pending", response_model=List[UserRead])
def get_pending_users(
    db: DBSession,
    admin: AdminUser
):
    """
    List all users waiting for authorization.
    Requires admin privileges.
    """
    return user_service.list_pending_users(db)

@router.post("/users/{user_id}/authorize", response_model=UserRead)
def authorize_user(
    user_id: int,
    db: DBSession,
    admin: AdminUser
):
    """
    Approve a specific user request.
    Requires admin privileges.
    """
    user = user_service.authorize_user(db, user_id=user_id, admin_id=admin.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/users/{user_id}/reject", response_model=UserRead)
def reject_user(
    user_id: int,
    db: DBSession,
    admin: AdminUser
):
    """
    Reject a specific user request.
    Requires admin privileges.
    """
    user = user_service.reject_user(db, user_id=user_id, admin_id=admin.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/users/{user_id}", response_model=UserRead)
def update_user_status(
    user_id: int,
    user_in: UserUpdate,
    db: DBSession,
    admin: AdminUser
):
    """
    Update a user's status or role.
    Requires admin privileges.
    """
    user = user_service.update_user(db, user_id=user_id, user_in=user_in)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
