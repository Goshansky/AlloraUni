"""Product service module for business logic."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


async def get_product_by_id(product_id: UUID, db: AsyncSession) -> Optional[Product]:
    """
    Get a product by ID.
    
    Args:
        product_id: Product ID
        db: Database session
        
    Returns:
        Product object if found, None otherwise
    """
    result = await db.execute(
        select(Product)
        .where(Product.id == product_id)
        .options(selectinload(Product.category))
    )
    return result.scalars().first()


async def get_products(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100,
    category_id: Optional[UUID] = None
) -> List[Product]:
    """
    Get a list of products.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        category_id: Filter by category ID
        
    Returns:
        List of Product objects
    """
    query = select(Product).options(selectinload(Product.category))
    
    if category_id:
        query = query.where(Product.category_id == category_id)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def create_product(product_in: ProductCreate, db: AsyncSession) -> Product:
    """
    Create a new product.
    
    Args:
        product_in: Product creation data
        db: Database session
        
    Returns:
        Created Product object
    """
    product = Product(
        title=product_in.title,
        description=product_in.description,
        price=product_in.price,
        image_url=product_in.image_url,
        stock=product_in.stock,
        category_id=product_in.category_id
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


async def update_product(
    product: Product, product_in: ProductUpdate, db: AsyncSession
) -> Product:
    """
    Update a product.
    
    Args:
        product: Product object to update
        product_in: Product update data
        db: Database session
        
    Returns:
        Updated Product object
    """
    update_data = product_in.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(product, field, value)
    
    await db.commit()
    await db.refresh(product)
    return product


async def delete_product(product: Product, db: AsyncSession) -> None:
    """
    Delete a product.
    
    Args:
        product: Product object to delete
        db: Database session
    """
    await db.delete(product)
    await db.commit() 