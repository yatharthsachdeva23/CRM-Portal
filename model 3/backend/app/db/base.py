"""
Database Base Configuration
SQLAlchemy base class and session management.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os

from app.core.config import settings


# Create engine with appropriate configuration
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=settings.DEBUG
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_size=20,
        max_overflow=0,
        echo=settings.DEBUG
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency for getting database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize database tables."""
    from app import models
    Base.metadata.create_all(bind=engine)
