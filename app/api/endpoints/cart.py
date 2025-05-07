"""Cart endpoints."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_user_dependency, get_db_dependency
from app.models.user import User
from app.schemas.cart import CartItemCreate, CartItemUpdate, CartResponse
from app.services.cart import (
    add_to_cart,
    calculate_cart_total,
    clear_cart,
    get_cart_item,
    get_cart_items,
    remove_from_cart,
    update_cart_item,
)
from app.services.product import get_product_by_id

router = APIRouter(tags=["cart"], prefix="/cart")


@router.get("", response_model=CartResponse)
async def read_cart(
    current_user: User = get_current_user_dependency(),
    db: AsyncSession = get_db_dependency(),
) -> CartResponse:
    """
    Get current user's cart.
    """
    cart_items = await get_cart_items(current_user.id, db)
    total_price = await calculate_cart_total(current_user.id, db)
    
    return CartResponse(
        items=cart_items,
        total_price=total_price
    )


@router.post("/add", response_model=CartResponse)
async def add_item_to_cart(
    item: CartItemCreate,
    current_user: User = get_current_user_dependency(),
    db: AsyncSession = get_db_dependency(),
) -> CartResponse:
    """
    Add item to cart.
    """
    # Check if product exists
    product = await get_product_by_id(item.product_id, db)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    
    # Check if product is in stock
    if product.stock < item.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough stock available",
        )
    
    # Add to cart
    await add_to_cart(current_user, item, db)
    
    # Return updated cart
    cart_items = await get_cart_items(current_user.id, db)
    total_price = await calculate_cart_total(current_user.id, db)
    
    return CartResponse(
        items=cart_items,
        total_price=total_price
    )


@router.post("/remove", response_model=CartResponse)
async def remove_item_from_cart(
    product_id: UUID,
    current_user: User = get_current_user_dependency(),
    db: AsyncSession = get_db_dependency(),
) -> CartResponse:
    """
    Remove item from cart.
    """
    # Check if item exists in cart
    cart_item = await get_cart_item(current_user.id, product_id, db)
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found in cart",
        )
    
    # Remove from cart
    await remove_from_cart(cart_item, db)
    
    # Return updated cart
    cart_items = await get_cart_items(current_user.id, db)
    total_price = await calculate_cart_total(current_user.id, db)
    
    return CartResponse(
        items=cart_items,
        total_price=total_price
    )


@router.post("/update", response_model=CartResponse)
async def update_item_in_cart(
    product_id: UUID,
    update_data: CartItemUpdate,
    current_user: User = get_current_user_dependency(),
    db: AsyncSession = get_db_dependency(),
) -> CartResponse:
    """
    Update item quantity in cart.
    """
    # Check if item exists in cart
    cart_item = await get_cart_item(current_user.id, product_id, db)
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found in cart",
        )
    
    # Check if quantity is valid
    product = await get_product_by_id(product_id, db)
    if update_data.quantity and update_data.quantity > product.stock:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough stock available",
        )
    
    # Update cart item
    await update_cart_item(cart_item, update_data, db)
    
    # Return updated cart
    cart_items = await get_cart_items(current_user.id, db)
    total_price = await calculate_cart_total(current_user.id, db)
    
    return CartResponse(
        items=cart_items,
        total_price=total_price
    )


@router.post("/clear", response_model=CartResponse)
async def clear_user_cart(
    current_user: User = get_current_user_dependency(),
    db: AsyncSession = get_db_dependency(),
) -> CartResponse:
    """
    Clear all items from cart.
    """
    await clear_cart(current_user.id, db)
    
    return CartResponse(
        items=[],
        total_price=0.0
    ) 