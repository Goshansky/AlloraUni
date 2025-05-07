"""Review endpoints."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_user_dependency, get_db_dependency
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewWithUser
from app.services.product import get_product_by_id
from app.services.review import (
    create_review,
    delete_review,
    get_reviews_by_product,
    get_user_review_for_product,
)

router = APIRouter(tags=["reviews"], prefix="/reviews")


@router.get("/{product_id}", response_model=List[ReviewWithUser])
async def read_product_reviews(
    product_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = get_db_dependency(),
) -> List[ReviewWithUser]:
    """
    Get reviews for a product.
    """
    # Check if product exists
    product = await get_product_by_id(product_id, db)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    
    reviews = await get_reviews_by_product(product_id, db, skip=skip, limit=limit)
    
    # Convert to ReviewWithUser
    result = []
    for review in reviews:
        result.append(
            ReviewWithUser(
                id=review.id,
                user_id=review.user_id,
                product_id=review.product_id,
                rating=review.rating,
                comment=review.comment,
                created_at=review.created_at,
                username=review.user.username
            )
        )
    
    return result


@router.post("/{product_id}", response_model=ReviewWithUser, status_code=status.HTTP_201_CREATED)
async def create_product_review(
    product_id: UUID,
    review_in: ReviewCreate,
    current_user: User = get_current_user_dependency(),
    db: AsyncSession = get_db_dependency(),
) -> ReviewWithUser:
    """
    Create or update a review for a product.
    """
    # Check if product exists
    product = await get_product_by_id(product_id, db)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    
    # Create or update review
    review = await create_review(current_user, product_id, review_in, db)
    
    # Return with username
    return ReviewWithUser(
        id=review.id,
        user_id=review.user_id,
        product_id=review.product_id,
        rating=review.rating,
        comment=review.comment,
        created_at=review.created_at,
        username=current_user.username
    )


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_review(
    product_id: UUID,
    current_user: User = get_current_user_dependency(),
    db: AsyncSession = get_db_dependency(),
) -> None:
    """
    Delete a review for a product.
    """
    # Check if product exists
    product = await get_product_by_id(product_id, db)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    
    # Check if review exists
    review = await get_user_review_for_product(current_user.id, product_id, db)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )
    
    # Delete review
    await delete_review(review, db) 