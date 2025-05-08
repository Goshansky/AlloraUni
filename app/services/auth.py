from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User


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