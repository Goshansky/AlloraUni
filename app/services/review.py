"""Review service module for business logic."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.review import Review
from app.models.user import User
from app.schemas.review import ReviewCreate


async def get_reviews_by_product(
    product_id: UUID, db: AsyncSession, skip: int = 0, limit: int = 100
) -> List[Review]:
    """
    Get reviews for a product.
    
    Args:
        product_id: Product ID
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of Review objects
    """
    result = await db.execute(
        select(Review)
        .where(Review.product_id == product_id)
        .options(selectinload(Review.user))
        .order_by(Review.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def get_review_by_id(review_id: UUID, db: AsyncSession) -> Optional[Review]:
    """
    Get a review by ID.
    
    Args:
        review_id: Review ID
        db: Database session
        
    Returns:
        Review object if found, None otherwise
    """
    result = await db.execute(
        select(Review)
        .where(Review.id == review_id)
        .options(selectinload(Review.user))
    )
    return result.scalars().first()


async def get_user_review_for_product(
    user_id: UUID, product_id: UUID, db: AsyncSession
) -> Optional[Review]:
    """
    Get a user's review for a product.
    
    Args:
        user_id: User ID
        product_id: Product ID
        db: Database session
        
    Returns:
        Review object if found, None otherwise
    """
    result = await db.execute(
        select(Review)
        .where(Review.user_id == user_id, Review.product_id == product_id)
    )
    return result.scalars().first()


async def create_review(
    user: User, product_id: UUID, review_in: ReviewCreate, db: AsyncSession
) -> Review:
    """
    Create a new review.
    
    Args:
        user: User object
        product_id: Product ID
        review_in: Review creation data
        db: Database session
        
    Returns:
        Created Review object
    """
    # Check if user already reviewed this product
    existing_review = await get_user_review_for_product(user.id, product_id, db)
    
    if existing_review:
        # Update existing review
        existing_review.rating = review_in.rating
        existing_review.comment = review_in.comment
        await db.commit()
        await db.refresh(existing_review)
        return existing_review
    
    # Create new review
    review = Review(
        user_id=user.id,
        product_id=product_id,
        rating=review_in.rating,
        comment=review_in.comment
    )
    db.add(review)
    await db.commit()
    await db.refresh(review)
    return review


async def delete_review(review: Review, db: AsyncSession) -> None:
    """
    Delete a review.
    
    Args:
        review: Review object to delete
        db: Database session
    """
    await db.delete(review)
    await db.commit() 