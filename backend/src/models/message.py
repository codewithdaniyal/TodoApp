"""
Message SQLModel for AI chat conversation history.

This module defines the Message entity for persisting chat conversations
in a stateless architecture. Messages are scoped by user_id and grouped
by thread_id (OpenAI Assistants API thread identifier).

CRITICAL SECURITY REQUIREMENT:
    All message queries MUST filter by user_id to enforce user isolation.
"""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class Message(SQLModel, table=True):
    """
    Message entity representing conversation history.

    Attributes:
        id: Unique message identifier (auto-generated primary key)
        user_id: Owner user reference (foreign key, indexed - CRITICAL)
        thread_id: OpenAI thread identifier (indexed for thread queries)
        role: Message sender ("user" or "assistant")
        content: Message text (1-4000 characters)
        tool_calls: JSON string of tool executions (assistant only, optional)
        created_at: Message creation timestamp (UTC)

    Indexes:
        - PRIMARY KEY on id
        - INDEX on user_id (CRITICAL for user isolation queries)
        - INDEX on thread_id (efficient thread-based queries)

    Foreign Key:
        - user_id references users.id (NOT NULL, ON DELETE CASCADE)

    Validation:
        - role: Must be "user" or "assistant" (application validates)
        - content: Non-empty, max 4000 characters
        - tool_calls: Valid JSON string or NULL
        - user_id: Must reference existing user

    Security:
        ALL queries must include: WHERE user_id = <authenticated_user_id>

    Example Usage:
        # Store user message
        user_msg = Message(
            user_id="user_123",
            thread_id="thread_abc",
            role="user",
            content="Create a task to buy groceries"
        )
        session.add(user_msg)
        session.commit()

        # Store assistant message with tool calls
        assistant_msg = Message(
            user_id="user_123",
            thread_id="thread_abc",
            role="assistant",
            content="I've created a task for you.",
            tool_calls='[{"tool":"create_task","args":{...}}]'
        )
        session.add(assistant_msg)
        session.commit()
    """
    __tablename__ = "messages"

    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="users.id")  # Changed from str to int to match users.id
    thread_id: str = Field(index=True)
    role: str  # "user" or "assistant"
    content: str  # Message text
    tool_calls: Optional[str] = Field(default=None)  # JSON string
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "thread_id": "thread_abc",
                "role": "user",
                "content": "Create a task to buy groceries",
                "tool_calls": None,
                "created_at": "2026-02-05T10:00:00Z"
            }
        }
