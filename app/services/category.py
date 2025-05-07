"""Category service module for business logic."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.category import Category
from app.models.product import Product
from app.schemas.category import CategoryCreate, CategoryUpdate


async def get_category_by_id(category_id: UUID, db: AsyncSession) -> Optional[Category]:
    """
    Get a category by ID.
    
    Args:
        category_id: Category ID
        db: Database session
        
    Returns:
        Category object if found, None otherwise
    """
    result = await db.execute(
        select(Category)
        .where(Category.id == category_id)
        .options(selectinload(Category.children))
    )
    return result.scalars().first()


async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Category]:
    """
    Get a list of categories.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of Category objects
    """
    result = await db.execute(
        select(Category)
        .options(selectinload(Category.children))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def get_categories_with_product_count(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> List[dict]:
    """
    Get categories with product count.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of categories with product count
    """
    subq = (
        select(Category.id, func.count(Product.id).label("products_count"))
        .outerjoin(Product, Category.id == Product.category_id)
        .group_by(Category.id)
        .subquery()
    )
    
    result = await db.execute(
        select(Category, subq.c.products_count)
        .outerjoin(subq, Category.id == subq.c.id)
        .options(selectinload(Category.children))
        .offset(skip)
        .limit(limit)
    )
    
    categories_with_count = []
    for category, count in result:
        category_dict = {
            "id": category.id,
            "name": category.name,
            "parent_id": category.parent_id,
            "products_count": count or 0
        }
        categories_with_count.append(category_dict)
    
    return categories_with_count


async def create_category(category_in: CategoryCreate, db: AsyncSession) -> Category:
    """
    Create a new category.
    
    Args:
        category_in: Category creation data
        db: Database session
        
    Returns:
        Created Category object
    """
    category = Category(
        name=category_in.name,
        parent_id=category_in.parent_id
    )
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


async def update_category(
    category: Category, category_in: CategoryUpdate, db: AsyncSession
) -> Category:
    """
    Update a category.
    
    Args:
        category: Category object to update
        category_in: Category update data
        db: Database session
        
    Returns:
        Updated Category object
    """
    update_data = category_in.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(category, field, value)
    
    await db.commit()
    await db.refresh(category)
    return category


async def delete_category(category: Category, db: AsyncSession) -> None:
    """
    Delete a category.
    
    Args:
        category: Category object to delete
        db: Database session
    """
    await db.delete(category)
    await db.commit() 