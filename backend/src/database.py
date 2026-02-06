"""
Database engine and session configuration for Neon PostgreSQL.

This module provides:
- SQLModel engine with Neon-optimized connection pooling
- Session dependency for FastAPI route injection
- Connection management for serverless environment

Environment Variables:
    DATABASE_URL: PostgreSQL connection string with format:
        postgresql://[user]:[password]@[host]/[db]?sslmode=require

Performance Configuration:
    - pool_pre_ping=True: Essential for Neon serverless (handles connection drops)
    - pool_size=5: Base persistent connections
    - max_overflow=10: Additional temporary connections (total max: 15)

Usage in FastAPI routes:
    @app.get("/tasks")
    def get_tasks(session: Session = Depends(get_session)):
        # Use session for database queries
        pass
"""

import os
from typing import Annotated, Generator
from sqlmodel import Session, SQLModel, create_engine
from fastapi import Depends

# Load environment variables
from dotenv import load_dotenv
load_dotenv()


def get_database_url() -> str:
    """
    Get database connection URL from environment.

    Returns:
        PostgreSQL connection string with SSL mode

    Raises:
        ValueError: If DATABASE_URL is not set
    """
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError(
            "DATABASE_URL environment variable is not set. "
            "Please configure it in .env file with format: "
            "postgresql://user:password@ep-host.neon.tech/dbname?sslmode=require"
        )
    return database_url


# Create SQLModel engine with Neon-optimized settings
engine = create_engine(
    get_database_url(),
    echo=True,  # Log SQL statements (set to False in production for performance)
    pool_pre_ping=True,  # CRITICAL: Verify connections before use (handles Neon serverless drops)
    pool_size=5,  # Base persistent connections in pool
    max_overflow=10,  # Additional temporary connections (total max: 15)
    pool_recycle=3600,  # Recycle connections after 1 hour (prevents stale connections)
)


def create_db_and_tables():
    """
    Create all database tables from SQLModel metadata.

    This should be called ONLY for initial setup or testing.
    In production, use Alembic migrations instead.

    Note:
        This function creates tables but does NOT create indexes.
        Use Alembic migrations to ensure all indexes (especially
        task.user_id index) are properly created.
    """
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.

    Yields a session that automatically commits on success
    and rolls back on exception.

    Usage:
        @app.get("/tasks")
        def get_tasks(session: Session = Depends(get_session)):
            # Use session here
            pass

    Yields:
        Session: SQLModel database session

    Session Lifecycle:
        1. Session created from engine
        2. Yielded to route handler
        3. Automatically closed after request (commit or rollback)
    """
    with Session(engine) as session:
        yield session


# Type alias for dependency injection
SessionDep = Annotated[Session, Depends(get_session)]


# Example usage in FastAPI routes:
"""
from fastapi import FastAPI
from .database import SessionDep

app = FastAPI()

@app.get("/tasks")
def list_tasks(session: SessionDep, user_id: int):
    # Session is automatically injected
    statement = select(Task).where(Task.user_id == user_id)
    tasks = session.exec(statement).all()
    return tasks
"""
