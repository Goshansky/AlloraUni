"""Order service module for business logic."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.order import Order, OrderItem
from app.models.user import User
from app.schemas.order import OrderUpdate
from app.services.cart import get_cart_items, calculate_cart_total, clear_cart


async def get_orders_by_user(user_id: UUID, db: AsyncSession) -> List[Order]:
    """
    Get orders for a user.
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        List of Order objects
    """
    result = await db.execute(
        select(Order)
        .where(Order.user_id == user_id)
        .options(
            selectinload(Order.items).selectinload(OrderItem.product)
        )
        .order_by(Order.created_at.desc())
    )
    return result.scalars().all()


async def get_order_by_id(order_id: UUID, db: AsyncSession) -> Optional[Order]:
    """
    Get an order by ID.
    
    Args:
        order_id: Order ID
        db: Database session
        
    Returns:
        Order object if found, None otherwise
    """
    result = await db.execute(
        select(Order)
        .where(Order.id == order_id)
        .options(
            selectinload(Order.items).selectinload(OrderItem.product)
        )
    )
    return result.scalars().first()


async def create_order_from_cart(user: User, db: AsyncSession) -> Optional[Order]:
    """
    Create an order from the user's cart.
    
    Args:
        user: User object
        db: Database session
        
    Returns:
        Created Order object, or None if cart is empty
    """
    # Get cart items
    cart_items = await get_cart_items(user.id, db)
    
    if not cart_items:
        return None
    
    # Calculate total price
    total_price = await calculate_cart_total(user.id, db)
    
    # Create order
    order = Order(
        user_id=user.id,
        status="pending",
        total_price=total_price
    )
    db.add(order)
    await db.flush()  # Flush to get the order ID
    
    # Create order items
    for cart_item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            unit_price=cart_item.product.price
        )
        db.add(order_item)
    
    # Clear cart
    await clear_cart(user.id, db)
    
    await db.commit()
    await db.refresh(order)
    return order


async def update_order_status(
    order: Order, order_update: OrderUpdate, db: AsyncSession
) -> Order:
    """
    Update an order's status.
    
    Args:
        order: Order object to update
        order_update: Order update data
        db: Database session
        
    Returns:
        Updated Order object
    """
    if order_update.status:
        order.status = order_update.status
    
    await db.commit()
    await db.refresh(order)
    return order 