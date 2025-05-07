"""Cart schemas module."""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.product import ProductResponse


# Shared properties
class CartItemBase(BaseModel):
    """Base CartItem schema."""
    product_id: UUID
    quantity: int = Field(..., gt=0)


# Properties to receive on cart item creation/update
class CartItemCreate(CartItemBase):
    """CartItem creation schema."""
    pass


class CartItemUpdate(BaseModel):
    """CartItem update schema."""
    quantity: Optional[int] = Field(None, gt=0)


# Properties to return to client
class CartItemResponse(CartItemBase):
    """CartItem response schema."""
    id: UUID
    user_id: UUID
    
    class Config:
        """Configuration for Pydantic model."""
        from_attributes = True


# Full cart response with products
class CartItemWithProduct(CartItemResponse):
    """CartItem with product details schema."""
    product: ProductResponse


class CartResponse(BaseModel):
    """Cart response schema."""
    items: List[CartItemWithProduct]
    total_price: float 