"""
Task SQLModel for multi-user Todo application.

This module defines the Task entity with strict user isolation.

CRITICAL SECURITY REQUIREMENT:
    All task queries MUST filter by user_id to enforce user isolation.
    Never query tasks without validating user ownership.

Performance Notes:
    - user_id is indexed for fast user-scoped queries
    - For 1000 tasks per user, single user query performs in <10ms
"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .user import User


class Task(SQLModel, table=True):
    """
    Task entity representing individual todo items owned by users.

    Attributes:
        id: Unique task identifier (auto-generated primary key)
        user_id: Owner user reference (foreign key, indexed - CRITICAL)
        title: Task description text (1-500 characters)
        completed: Completion status (default: false)
        created_at: Task creation timestamp (UTC)
        updated_at: Last modification timestamp (UTC, manually updated)
        user: Relationship back to User entity

    Indexes:
        - PRIMARY KEY on id
        - INDEX on user_id (CRITICAL for user isolation queries)

    Foreign Key:
        - user_id references users.id (NOT NULL)

    Validation:
        - title: Non-empty string, maximum 500 characters (FR-010, FR-023)
        - user_id: Must reference existing user (foreign key constraint)
        - completed: Boolean only (true/false)
        - All timestamps in UTC timezone

    Security:
        ALL queries must include: WHERE user_id = <authenticated_user_id>
        This prevents cross-user data leakage.
    """

    __tablename__ = "tasks"

    # Primary key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Task content
    title: str = Field(
        min_length=1,
        max_length=500,
        description="Task description text (1-500 characters)"
    )
    completed: bool = Field(
        default=False,
        description="Task completion status"
    )

    # Foreign key with index - CRITICAL for user isolation
    user_id: int = Field(
        foreign_key="users.id",
        index=True,  # Essential for query performance
        description="Owner user reference (indexed for performance)"
    )

    # Timestamps (UTC)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Task creation timestamp (UTC)"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last modification timestamp (UTC, manually updated on PUT)"
    )

    # Relationship back to User
    user: "User" = Relationship(back_populates="tasks")


# Example correct query patterns (for reference):
"""
✅ CORRECT - Get all tasks for authenticated user:
    statement = select(Task).where(Task.user_id == user_id)
    tasks = session.exec(statement).all()

✅ CORRECT - Get specific task with ownership check:
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id  # Ownership validation
    )
    task = session.exec(statement).first()

❌ INCORRECT - Exposes all users' tasks (SECURITY VULNERABILITY):
    statement = select(Task)  # Missing user_id filter!
    tasks = session.exec(statement).all()

❌ INCORRECT - Trusts client-provided user_id:
    statement = select(Task).where(Task.user_id == request.user_id)
    # Should use user_id from JWT token, not request body
"""
