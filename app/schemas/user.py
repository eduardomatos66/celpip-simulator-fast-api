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
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
