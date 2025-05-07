"""Authentication related dependencies."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user, get_current_active_admin
from app.db.base import get_db
from app.models.user import User


def get_current_user_dependency():
    """Dependency for getting the current user."""
    return Depends(get_current_user)


def get_current_admin_dependency():
    """Dependency for getting the current admin user."""
    return Depends(get_current_active_admin)


def get_db_dependency():
    """Dependency for getting the database session."""
    return Depends(get_db) 