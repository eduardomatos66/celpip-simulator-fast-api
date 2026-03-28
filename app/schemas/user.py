from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional
from app.models.user import UserStatus

class UserBase(BaseModel):
    full_name: str
    email: EmailStr

class UserCreate(UserBase):
    clerk_id: str

class UserRead(UserBase):
    id: int
    clerk_id: str
    status: UserStatus
    is_admin: bool
    authorized_at: Optional[datetime] = None
    authorized_by_admin_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    status: Optional[UserStatus] = None
    is_admin: Optional[bool] = None
