from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate

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
        user_in = UserCreate(full_name=full_name, email=email, clerk_id=clerk_id)
        user = create_user(db, user_in)
    return user
