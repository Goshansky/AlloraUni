"""Product endpoints."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_admin_dependency, get_db_dependency
from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.services.product import (
    create_product,
    delete_product,
    get_product_by_id,
    get_products,
    update_product,
)

router = APIRouter(tags=["products"], prefix="/products")


@router.get("", response_model=List[ProductResponse])
async def read_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category_id: Optional[UUID] = None,
    db: AsyncSession = get_db_dependency(),
) -> List[ProductResponse]:
    """
    Get list of products.
    """
    products = await get_products(db, skip=skip, limit=limit, category_id=category_id)
    return products


@router.get("/{product_id}", response_model=ProductResponse)
async def read_product(
    product_id: UUID,
    db: AsyncSession = get_db_dependency(),
) -> ProductResponse:
    """
    Get a product by ID.
    """
    product = await get_product_by_id(product_id, db)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return product


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_new_product(
    product_in: ProductCreate,
    db: AsyncSession = get_db_dependency(),
    current_user: User = get_current_admin_dependency(),
) -> ProductResponse:
    """
    Create a new product (admin only).
    """
    product = await create_product(product_in, db)
    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_existing_product(
    product_id: UUID,
    product_in: ProductUpdate,
    db: AsyncSession = get_db_dependency(),
    current_user: User = get_current_admin_dependency(),
) -> ProductResponse:
    """
    Update a product (admin only).
    """
    product = await get_product_by_id(product_id, db)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    
    updated_product = await update_product(product, product_in, db)
    return updated_product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_product(
    product_id: UUID,
    db: AsyncSession = get_db_dependency(),
    current_user: User = get_current_admin_dependency(),
) -> None:
    """
    Delete a product (admin only).
    """
    product = await get_product_by_id(product_id, db)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    
    await delete_product(product, db) 