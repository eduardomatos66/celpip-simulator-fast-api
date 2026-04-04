from pydantic import BaseModel, EmailStr, ConfigDict, Field
from datetime import datetime
from typing import Optional
from app.models.user import UserStatus

class UserBase(BaseModel):
    full_name: str = Field(..., description="The user's full name", examples=["John Doe"])
    email: EmailStr = Field(..., description="The user's primary email address", examples=["john.doe@example.com"])

class UserCreate(UserBase):
    clerk_id: str = Field(..., description="The unique identity provider ID from Clerk", examples=["user_2N7X..."])

class UserRead(UserBase):
    id: int = Field(..., description="Internal database unique identifier")
    clerk_id: str = Field(..., description="The unique identity provider ID from Clerk")
    status: UserStatus = Field(..., description="Current status of the user (PENDING, APPROVED, REJECTED)")
    is_admin: bool = Field(..., description="Whether the user has administrative privileges")
    authorized_at: Optional[datetime] = Field(None, description="Timestamp when the user was authorized")
    authorized_by_admin_id: Optional[int] = Field(None, description="The ID of the admin who authorized this user")
    created_at: datetime = Field(..., description="Timestamp when the user record was created")
    updated_at: Optional[datetime] = Field(None, description="Timestamp of the last update to the user record")

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, description="Update the user's full name")
    status: Optional[UserStatus] = Field(None, description="Update the user's status (Admin only)")
    is_admin: Optional[bool] = Field(None, description="Update admin privileges (Admin only)")
