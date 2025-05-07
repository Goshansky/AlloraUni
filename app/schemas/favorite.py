"""Favorite schemas module."""

from typing import List
from uuid import UUID

from pydantic import BaseModel

from app.schemas.product import ProductResponse


# Shared properties
class FavoriteBase(BaseModel):
    """Base Favorite schema."""
    product_id: UUID


# Properties to receive on favorite creation
class FavoriteCreate(FavoriteBase):
    """Favorite creation schema."""
    pass


# Properties to return to client
class FavoriteResponse(FavoriteBase):
    """Favorite response schema."""
    id: UUID
    user_id: UUID
    
    class Config:
        """Configuration for Pydantic model."""
        from_attributes = True


# Favorite with product details
class FavoriteWithProduct(FavoriteResponse):
    """Favorite with product details schema."""
    product: ProductResponse


# User's favorites list
class FavoritesList(BaseModel):
    """User's favorites list schema."""
    favorites: List[FavoriteWithProduct] 