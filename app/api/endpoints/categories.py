"""Category endpoints."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_admin_dependency, get_db_dependency
from app.models.user import User
from app.schemas.category import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
    CategoryWithProductsCount,
)
from app.schemas.product import ProductResponse
from app.services.category import (
    create_category,
    delete_category,
    get_categories,
    get_categories_with_product_count,
    get_category_by_id,
    update_category,
)
from app.services.product import get_products

router = APIRouter(tags=["categories"], prefix="/categories")


@router.get("", response_model=List[CategoryWithProductsCount])
async def read_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = get_db_dependency(),
) -> List[CategoryWithProductsCount]:
    """
    Get list of categories with product counts.
    """
    categories = await get_categories_with_product_count(db, skip=skip, limit=limit)
    return categories


@router.get("/{category_id}", response_model=CategoryResponse)
async def read_category(
    category_id: UUID,
    db: AsyncSession = get_db_dependency(),
) -> CategoryResponse:
    """
    Get a category by ID.
    """
    category = await get_category_by_id(category_id, db)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    return category


@router.get("/{category_id}/products", response_model=List[ProductResponse])
async def read_category_products(
    category_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = get_db_dependency(),
) -> List[ProductResponse]:
    """
    Get products by category.
    """
    category = await get_category_by_id(category_id, db)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    
    products = await get_products(db, skip=skip, limit=limit, category_id=category_id)
    return products


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_new_category(
    category_in: CategoryCreate,
    db: AsyncSession = get_db_dependency(),
    current_user: User = get_current_admin_dependency(),
) -> CategoryResponse:
    """
    Create a new category (admin only).
    """
    # Check if parent category exists
    if category_in.parent_id:
        parent_category = await get_category_by_id(category_in.parent_id, db)
        if not parent_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent category not found",
            )
    
    category = await create_category(category_in, db)
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_existing_category(
    category_id: UUID,
    category_in: CategoryUpdate,
    db: AsyncSession = get_db_dependency(),
    current_user: User = get_current_admin_dependency(),
) -> CategoryResponse:
    """
    Update a category (admin only).
    """
    category = await get_category_by_id(category_id, db)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    
    # Check if parent category exists
    if category_in.parent_id:
        parent_category = await get_category_by_id(category_in.parent_id, db)
        if not parent_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent category not found",
            )
        
        # Prevent circular reference
        if category_in.parent_id == category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category cannot be its own parent",
            )
    
    updated_category = await update_category(category, category_in, db)
    return updated_category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_category(
    category_id: UUID,
    db: AsyncSession = get_db_dependency(),
    current_user: User = get_current_admin_dependency(),
) -> None:
    """
    Delete a category (admin only).
    """
    category = await get_category_by_id(category_id, db)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    
    # Check if category has subcategories
    if category.children:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete category with subcategories",
        )
    
    # Check if category has products
    products = await get_products(db, category_id=category_id, limit=1)
    if products:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete category with products",
        )
    
    await delete_category(category, db) 