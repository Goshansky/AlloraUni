"""User schemas module."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# Shared properties
class UserBase(BaseModel):
    """Base User schema."""
    email: EmailStr
    username: str
    is_active: Optional[bool] = True
    is_admin: Optional[bool] = False


# Properties to receive on user creation
class UserCreate(UserBase):
    """User creation schema."""
    email: EmailStr
    username: str
    password: str = Field(..., min_length=8)


# Properties to receive on user update
class UserUpdate(BaseModel):
    """User update schema."""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)


# Properties to return to client
class UserResponse(UserBase):
    """User response schema."""
    id: UUID
    created_at: datetime
    
    class Config:
        """Configuration for Pydantic model."""
        from_attributes = True


# Properties for token
class Token(BaseModel):
    """Token schema."""
    access_token: str
    refresh_token: str
    token_type: str


class TokenPayload(BaseModel):
    """Token payload schema."""
    sub: str
    exp: int
    type: str


# Properties for user login
class UserLogin(BaseModel):
    """User login schema."""
    email: EmailStr
    password: str 