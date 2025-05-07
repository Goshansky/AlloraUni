"""Category model module."""

import uuid

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Category(Base):
    """Category model for SQLAlchemy."""
    
    __tablename__ = "categories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, index=True, unique=True, nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    
    # Self-referential relationship for parent-child categories
    children = relationship("Category", 
                          backref="parent",
                          remote_side=[id])
    
    # Products in this category
    products = relationship("Product", back_populates="category") 