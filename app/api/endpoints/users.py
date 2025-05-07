"""User endpoints."""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_user_dependency, get_db_dependency
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.services.user import update_user

router = APIRouter(tags=["users"], prefix="/users")


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user: User = get_current_user_dependency(),
) -> UserResponse:
    """
    Get current user information.
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_in: UserUpdate,
    current_user: User = get_current_user_dependency(),
    db: AsyncSession = get_db_dependency(),
) -> UserResponse:
    """
    Update current user.
    """
    # Check if email is already taken
    if user_in.email and user_in.email != current_user.email:
        # Check if email exists in the database
        from app.services.user import get_user_by_email
        
        existing_user = await get_user_by_email(user_in.email, db)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
    
    # Update user
    updated_user = await update_user(current_user, user_in, db)
    return updated_user 