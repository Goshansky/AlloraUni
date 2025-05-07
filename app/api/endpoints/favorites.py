"""Favorites endpoints."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_user_dependency, get_db_dependency
from app.models.user import User
from app.schemas.favorite import FavoritesList, FavoriteWithProduct
from app.services.favorite import (
    add_favorite,
    get_favorite,
    get_favorites_by_user,
    remove_favorite,
)
from app.services.product import get_product_by_id

router = APIRouter(tags=["favorites"], prefix="/favorites")


@router.get("", response_model=FavoritesList)
async def read_favorites(
    current_user: User = get_current_user_dependency(),
    db: AsyncSession = get_db_dependency(),
) -> FavoritesList:
    """
    Get user's favorites list.
    """
    favorites = await get_favorites_by_user(current_user.id, db)
    return FavoritesList(favorites=favorites)


@router.post("/{product_id}", response_model=FavoriteWithProduct, status_code=status.HTTP_201_CREATED)
async def add_to_favorites(
    product_id: UUID,
    current_user: User = get_current_user_dependency(),
    db: AsyncSession = get_db_dependency(),
) -> FavoriteWithProduct:
    """
    Add a product to favorites.
    """
    # Check if product exists
    product = await get_product_by_id(product_id, db)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    
    # Add to favorites
    favorite = await add_favorite(current_user, product_id, db)
    
    # Refresh to get product details
    await db.refresh(favorite)
    
    return favorite


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_favorites(
    product_id: UUID,
    current_user: User = get_current_user_dependency(),
    db: AsyncSession = get_db_dependency(),
) -> None:
    """
    Remove a product from favorites.
    """
    # Check if product is in favorites
    favorite = await get_favorite(current_user.id, product_id, db)
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not in favorites",
        )
    
    # Remove from favorites
    await remove_favorite(favorite, db) 