"""Product schemas module."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Shared properties
class ProductBase(BaseModel):
    """Base Product schema."""
    title: str
    description: str
    price: float = Field(..., gt=0)
    image_url: Optional[str] = None
    stock: int = Field(..., ge=0)
    category_id: UUID


# Properties to receive on product creation
class ProductCreate(ProductBase):
    """Product creation schema."""
    pass


# Properties to receive on product update
class ProductUpdate(BaseModel):
    """Product update schema."""
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    image_url: Optional[str] = None
    stock: Optional[int] = Field(None, ge=0)
    category_id: Optional[UUID] = None


# Properties to return to client
class ProductResponse(ProductBase):
    """Product response schema."""
    id: UUID
    created_at: datetime
    
    class Config:
        """Configuration for Pydantic model."""
        from_attributes = True 