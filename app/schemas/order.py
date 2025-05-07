"""Order schemas module."""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.product import ProductResponse


class OrderStatus(str, Enum):
    """Order status enum."""
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# Order Item schemas
class OrderItemBase(BaseModel):
    """Base OrderItem schema."""
    product_id: UUID
    quantity: int = Field(..., gt=0)


class OrderItemResponse(OrderItemBase):
    """OrderItem response schema."""
    id: UUID
    unit_price: float
    
    class Config:
        """Configuration for Pydantic model."""
        from_attributes = True


class OrderItemWithProduct(OrderItemResponse):
    """OrderItem with product details."""
    product: ProductResponse


# Order schemas
class OrderCreate(BaseModel):
    """Order creation schema."""
    pass  # Cart will be converted to an order


class OrderUpdate(BaseModel):
    """Order update schema."""
    status: Optional[OrderStatus] = None


class OrderResponse(BaseModel):
    """Order response schema."""
    id: UUID
    user_id: UUID
    status: OrderStatus
    total_price: float
    created_at: datetime
    
    class Config:
        """Configuration for Pydantic model."""
        from_attributes = True


class OrderWithItems(OrderResponse):
    """Order with order items."""
    items: List[OrderItemWithProduct]
 