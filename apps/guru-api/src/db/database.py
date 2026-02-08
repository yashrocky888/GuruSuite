"""
Database connection and session management.

This module sets up SQLAlchemy database connection, session factory,
and provides dependency injection for FastAPI routes.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from src.config import settings

# Create database engine with lazy connection
# pool_pre_ping=False prevents connection attempts at import time
# This allows the API to run without a database
engine = create_engine(
    settings.database_url,
    pool_pre_ping=False,  # Disable pre-ping to allow running without DB
    connect_args={"connect_timeout": 2},  # Fast timeout for connection attempts
    echo=settings.debug  # Log SQL queries in debug mode
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function for FastAPI routes to get database session.
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

