from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.user import User, UserStatus
from app.schemas.user import UserCreate, UserUpdate
from app.core.decorators import log_execution_time
from app.core.config import settings
from app.core import email as email_service
import httpx
from app.core.logger import logger

@log_execution_time
def get_user_by_clerk_id(db: Session, clerk_id: str) -> Optional[User]:
    return db.query(User).filter(User.clerk_id == clerk_id).first()

@log_execution_time
def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

@log_execution_time
def create_user(db: Session, user_in: UserCreate) -> User:
    user = User(
        full_name=user_in.full_name,
        email=user_in.email,
        clerk_id=user_in.clerk_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@log_execution_time
def get_or_create_user(db: Session, clerk_id: str, email: str, full_name: str) -> User:
    """Helper to ensure the user exists in our DB during login/token usage."""
    user = get_user_by_clerk_id(db, clerk_id)
    if not user:
        # Check if this is the first user ever
        first_user = db.query(User).first() is None
        
        user_in = UserCreate(full_name=full_name, email=email, clerk_id=clerk_id)
        user = create_user(db, user_in)
        
        if first_user:
            # Bootstrap first user as authorized admin
            user.is_admin = True
            user.status = UserStatus.APPROVED
            user.authorized_at = datetime.now()
            db.commit()
            db.refresh(user)
            # No email for the first system admin, or send a special one if needed
        else:
            # Send notification that review is pending
            email_service.send_pending_email(user.email, user.full_name)
            
    return user

@log_execution_time
def list_pending_users(db: Session):
    """List users waiting for authorization."""
    return db.query(User).filter(User.status == UserStatus.PENDING).all()

@log_execution_time
def authorize_user(db: Session, user_id: int, admin_id: int) -> Optional[User]:
    """Authorize a user by an admin."""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.status = UserStatus.APPROVED
        user.authorized_at = datetime.now()
        user.authorized_by_admin_id = admin_id
        db.commit()
        db.refresh(user)
        
        # Notify user
        email_service.send_approval_email(user.email, user.full_name)
        
        # Sync with Clerk
        _sync_user_to_clerk(user)
        
    return user

@log_execution_time
def reject_user(db: Session, user_id: int, admin_id: int) -> Optional[User]:
    """Reject a user request by an admin."""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.status = UserStatus.REJECTED
        user.authorized_at = datetime.now()
        user.authorized_by_admin_id = admin_id
        db.commit()
        db.refresh(user)
        
        # Notify user
        email_service.send_rejection_email(user.email, user.full_name)
        
        # Sync with Clerk
        _sync_user_to_clerk(user)
        
    return user

def _sync_user_to_clerk(user: User):
    """
    Sync certain DB fields to Clerk public_metadata.
    """
    if not settings.CLERK_SECRET_KEY:
        logger.warning(f"CLERK_SECRET_KEY not set, skipping sync for {user.email}")
        return

    # Map our local status to public metadata
    metadata = {
        "status": user.status,
        "is_admin": user.is_admin
    }

    try:
        url = f"https://api.clerk.com/v1/users/{user.clerk_id}"
        headers = {
            "Authorization": f"Bearer {settings.CLERK_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        with httpx.Client() as client:
            response = client.patch(url, json={"public_metadata": metadata}, headers=headers)
            if response.status_code == 200:
                logger.info(f"Successfully synced metadata to Clerk for {user.email}")
            else:
                logger.error(f"Failed to sync metadata to Clerk for {user.email}: {response.text}")
    except Exception as e:
        logger.error(f"Error during Clerk metadata sync: {e}")

@log_execution_time
def update_user(db: Session, user_id: int, user_in: UserUpdate) -> Optional[User]:
    """Update user fields."""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        update_data = user_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        db.commit()
        db.refresh(user)
    return user
