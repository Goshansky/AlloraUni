"""Favorite service module for business logic."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.favorite import Favorite
from app.models.user import User


async def get_favorites_by_user(user_id: UUID, db: AsyncSession) -> List[Favorite]:
    """
    Get favorites for a user.
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        List of Favorite objects
    """
    result = await db.execute(
        select(Favorite)
        .where(Favorite.user_id == user_id)
        .options(selectinload(Favorite.product))
    )
    return result.scalars().all()


async def get_favorite(
    user_id: UUID, product_id: UUID, db: AsyncSession
) -> Optional[Favorite]:
    """
    Get a specific favorite for a user.
    
    Args:
        user_id: User ID
        product_id: Product ID
        db: Database session
        
    Returns:
        Favorite object if found, None otherwise
    """
    result = await db.execute(
        select(Favorite)
        .where(Favorite.user_id == user_id, Favorite.product_id == product_id)
    )
    return result.scalars().first()


async def add_favorite(user: User, product_id: UUID, db: AsyncSession) -> Favorite:
    """
    Add a product to favorites.
    
    Args:
        user: User object
        product_id: Product ID
        db: Database session
        
    Returns:
        Created Favorite object
    """
    # Check if already favorited
    existing_favorite = await get_favorite(user.id, product_id, db)
    
    if existing_favorite:
        return existing_favorite
    
    # Create new favorite
    favorite = Favorite(
        user_id=user.id,
        product_id=product_id
    )
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    return favorite


async def remove_favorite(favorite: Favorite, db: AsyncSession) -> None:
    """
    Remove a product from favorites.
    
    Args:
        favorite: Favorite object to remove
        db: Database session
    """
    await db.delete(favorite)
    await db.commit() 