"""Cart service module for business logic."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.cart import CartItem
from app.models.user import User
from app.schemas.cart import CartItemCreate, CartItemUpdate


async def get_cart_items(user_id: UUID, db: AsyncSession) -> List[CartItem]:
    """
    Get cart items for a user.
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        List of CartItem objects
    """
    result = await db.execute(
        select(CartItem)
        .where(CartItem.user_id == user_id)
        .options(selectinload(CartItem.product))
    )
    return result.scalars().all()


async def get_cart_item(
    user_id: UUID, product_id: UUID, db: AsyncSession
) -> Optional[CartItem]:
    """
    Get a specific cart item for a user.
    
    Args:
        user_id: User ID
        product_id: Product ID
        db: Database session
        
    Returns:
        CartItem object if found, None otherwise
    """
    result = await db.execute(
        select(CartItem)
        .where(CartItem.user_id == user_id, CartItem.product_id == product_id)
        .options(selectinload(CartItem.product))
    )
    return result.scalars().first()


async def add_to_cart(
    user: User, cart_item_in: CartItemCreate, db: AsyncSession
) -> CartItem:
    """
    Add an item to the cart.
    
    Args:
        user: User object
        cart_item_in: Cart item creation data
        db: Database session
        
    Returns:
        Created or updated CartItem object
    """
    # Check if item already exists in cart
    existing_item = await get_cart_item(user.id, cart_item_in.product_id, db)
    
    if existing_item:
        # Update quantity
        existing_item.quantity += cart_item_in.quantity
        await db.commit()
        await db.refresh(existing_item)
        return existing_item
    
    # Create new cart item
    cart_item = CartItem(
        user_id=user.id,
        product_id=cart_item_in.product_id,
        quantity=cart_item_in.quantity
    )
    db.add(cart_item)
    await db.commit()
    await db.refresh(cart_item)
    return cart_item


async def update_cart_item(
    cart_item: CartItem, cart_item_in: CartItemUpdate, db: AsyncSession
) -> CartItem:
    """
    Update a cart item.
    
    Args:
        cart_item: CartItem object to update
        cart_item_in: Cart item update data
        db: Database session
        
    Returns:
        Updated CartItem object
    """
    update_data = cart_item_in.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(cart_item, field, value)
    
    await db.commit()
    await db.refresh(cart_item)
    return cart_item


async def remove_from_cart(cart_item: CartItem, db: AsyncSession) -> None:
    """
    Remove an item from the cart.
    
    Args:
        cart_item: CartItem object to remove
        db: Database session
    """
    await db.delete(cart_item)
    await db.commit()


async def clear_cart(user_id: UUID, db: AsyncSession) -> None:
    """
    Clear all items from a user's cart.
    
    Args:
        user_id: User ID
        db: Database session
    """
    cart_items = await get_cart_items(user_id, db)
    for item in cart_items:
        await db.delete(item)
    await db.commit()


async def calculate_cart_total(user_id: UUID, db: AsyncSession) -> float:
    """
    Calculate the total price of items in a user's cart.
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        Total price
    """
    cart_items = await get_cart_items(user_id, db)
    total = 0.0
    
    for item in cart_items:
        total += item.product.price * item.quantity
    
    return total 