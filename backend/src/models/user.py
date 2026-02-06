"""
User SQLModel for multi-user Todo application.

This module defines the User entity with authentication credentials
and relationship to tasks (1:N).

Security Notes:
- Passwords are pre-hashed by Better Auth before storage
- Email uniqueness enforced at database level
- created_at uses UTC timezone for consistency
"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .task import Task


class User(SQLModel, table=True):
    """
    User entity representing authenticated user accounts.

    Attributes:
        id: Unique user identifier (auto-generated primary key)
        email: User's email address for signin (unique, indexed)
        hashed_password: Bcrypt/Argon2 hashed password from Better Auth
        created_at: Account creation timestamp (UTC)
        tasks: Relationship to user's tasks (lazy-loaded)

    Indexes:
        - PRIMARY KEY on id
        - UNIQUE INDEX on email (for login lookups and uniqueness)

    Validation:
        - Email format validated by Better Auth and Pydantic
        - Password minimum 8 characters enforced by Better Auth
        - Email uniqueness enforced at database level
    """

    __tablename__ = "users"

    # Primary key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Authentication fields
    email: str = Field(
        unique=True,
        index=True,
        max_length=255,
        description="User's email address (unique identifier)"
    )
    hashed_password: str = Field(
        max_length=255,
        description="Bcrypt/Argon2 hashed password"
    )

    # Timestamp
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Account creation timestamp (UTC)"
    )

    # Relationship to tasks (1:N)
    tasks: list["Task"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"lazy": "select"}  # Lazy-load, not fetched by default
    )
