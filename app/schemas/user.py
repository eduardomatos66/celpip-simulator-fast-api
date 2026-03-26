from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    full_name: str
    email: EmailStr

class UserCreate(UserBase):
    clerk_id: str

class UserRead(UserBase):
    id: int
    clerk_id: str
    is_authorized: bool
    is_admin: bool
    authorized_at: Optional[datetime] = None
    authorized_by_admin_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    is_authorized: Optional[bool] = None
    is_admin: Optional[bool] = None
