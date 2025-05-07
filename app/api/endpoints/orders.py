"""Order endpoints."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_user_dependency, get_db_dependency
from app.models.user import User
from app.schemas.order import OrderResponse, OrderUpdate, OrderWithItems
from app.services.order import (
    create_order_from_cart,
    get_order_by_id,
    get_orders_by_user,
    update_order_status,
)

router = APIRouter(tags=["orders"], prefix="/orders")


@router.get("", response_model=List[OrderResponse])
async def read_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = get_current_user_dependency(),
    db: AsyncSession = get_db_dependency(),
) -> List[OrderResponse]:
    """
    Get list of user's orders.
    """
    orders = await get_orders_by_user(current_user.id, db)
    return orders[skip : skip + limit]


@router.get("/{order_id}", response_model=OrderWithItems)
async def read_order(
    order_id: UUID,
    current_user: User = get_current_user_dependency(),
    db: AsyncSession = get_db_dependency(),
) -> OrderWithItems:
    """
    Get an order by ID.
    """
    order = await get_order_by_id(order_id, db)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    
    # Check if order belongs to user or user is admin
    if order.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this order",
        )
    
    return order


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    current_user: User = get_current_user_dependency(),
    db: AsyncSession = get_db_dependency(),
) -> OrderResponse:
    """
    Create an order from the current user's cart.
    """
    order = await create_order_from_cart(current_user, db)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty",
        )
    
    return order


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: UUID,
    order_in: OrderUpdate,
    current_user: User = get_current_user_dependency(),
    db: AsyncSession = get_db_dependency(),
) -> OrderResponse:
    """
    Update an order status (admin only).
    """
    # Only admins can update orders
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update orders",
        )
    
    order = await get_order_by_id(order_id, db)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    
    updated_order = await update_order_status(order, order_in, db)
    return updated_order 