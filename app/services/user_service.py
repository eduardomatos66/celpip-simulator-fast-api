from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

def get_user_by_clerk_id(db: Session, clerk_id: str) -> Optional[User]:
    return db.query(User).filter(User.clerk_id == clerk_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

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
            user.is_authorized = True
            user.authorized_at = datetime.now()
            db.commit()
            db.refresh(user)
            
    return user

def list_pending_users(db: Session):
    """List users waiting for authorization."""
    return db.query(User).filter(User.is_authorized == False).all()

def authorize_user(db: Session, user_id: int, admin_id: int) -> Optional[User]:
    """Authorize a user by an admin."""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.is_authorized = True
        user.authorized_at = datetime.now()
        user.authorized_by_admin_id = admin_id
        db.commit()
        db.refresh(user)
    return user

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
