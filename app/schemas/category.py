"""Category schemas module."""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


# Shared properties
class CategoryBase(BaseModel):
    """Base Category schema."""
    name: str
    parent_id: Optional[UUID] = None


# Properties to receive on category creation
class CategoryCreate(CategoryBase):
    """Category creation schema."""
    pass


# Properties to receive on category update
class CategoryUpdate(BaseModel):
    """Category update schema."""
    name: Optional[str] = None
    parent_id: Optional[UUID] = None


# Properties to return to client
class CategoryResponse(CategoryBase):
    """Category response schema."""
    id: UUID
    
    class Config:
        """Configuration for Pydantic model."""
        from_attributes = True


# Properties to return to client with product count
class CategoryWithProductsCount(CategoryResponse):
    """Category schema with product count."""
    products_count: int 