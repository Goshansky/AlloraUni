"""Review schemas module."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Shared properties
class ReviewBase(BaseModel):
    """Base Review schema."""
    rating: int = Field(..., ge=1, le=5)
    comment: str


# Properties to receive on review creation
class ReviewCreate(ReviewBase):
    """Review creation schema."""
    pass


# Properties to return to client
class ReviewResponse(ReviewBase):
    """Review response schema."""
    id: UUID
    user_id: UUID
    product_id: UUID
    created_at: datetime
    
    class Config:
        """Configuration for Pydantic model."""
        from_attributes = True


# Properties to return with username
class ReviewWithUser(ReviewResponse):
    """Review with username schema."""
    username: str 