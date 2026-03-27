"""
User Models
Role-Based Access Control models for PS-CRM.
"""

from sqlalchemy import Column, Integer, String, Enum, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum

from app.db.base import Base

class UserRole(str, PyEnum):
    CITIZEN = "citizen"
    ADMIN = "admin"
    WORKER = "worker"

class User(Base):
    """
    Unified User model for Citizens, Admins, and Field Workers.
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.CITIZEN)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    # Link to worker details if role is worker
    worker_profile = relationship("Worker", back_populates="user", uselist=False)
