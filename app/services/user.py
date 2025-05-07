"""User service module for business logic."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


async def get_user_by_email(email: str, db: AsyncSession = None) -> Optional[User]:
    """
    Get a user by email.
    
    Args:
        email: User's email
        db: Database session
        
    Returns:
        User object if found, None otherwise
    """
    if db:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalars().first()
    return None


async def get_user_by_id(user_id: UUID, db: AsyncSession) -> Optional[User]:
    """
    Get a user by ID.
    
    Args:
        user_id: User's ID
        db: Database session
        
    Returns:
        User object if found, None otherwise
    """
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()


async def create_user(user_in: UserCreate, db: AsyncSession) -> User:
    """
    Create a new user.
    
    Args:
        user_in: User creation data
        db: Database session
        
    Returns:
        Created User object
    """
    hashed_password = get_password_hash(user_in.password)
    user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=hashed_password,
        is_active=user_in.is_active,
        is_admin=user_in.is_admin
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(email: str, password: str, db: AsyncSession) -> Optional[User]:
    """
    Authenticate a user.
    
    Args:
        email: User's email
        password: User's password
        db: Database session
        
    Returns:
        User object if authentication succeeds, None otherwise
    """
    user = await get_user_by_email(email, db)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def update_user(user: User, user_in: UserUpdate, db: AsyncSession) -> User:
    """
    Update a user.
    
    Args:
        user: User object to update
        user_in: User update data
        db: Database session
        
    Returns:
        Updated User object
    """
    update_data = user_in.model_dump(exclude_unset=True)
    
    if update_data.get("password"):
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    await db.commit()
    await db.refresh(user)
    return user 