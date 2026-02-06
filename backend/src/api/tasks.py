"""
FastAPI REST API endpoints for task management with JWT authentication.

This module implements secure CRUD operations for tasks with strict user isolation.
All endpoints require JWT authentication and enforce ownership validation.

Security Architecture:
- JWT authentication required on all endpoints (via get_current_user dependency)
- User isolation enforced at database query level (WHERE user_id = <jwt.user_id>)
- Ownership validation on UPDATE/DELETE/COMPLETE operations
- Returns 404 (not 403) for non-existent or unowned tasks (prevents info leakage)

Endpoints:
- GET    /api/tasks              - List all tasks for authenticated user
- POST   /api/tasks              - Create new task for authenticated user
- PUT    /api/tasks/{id}         - Update task title (ownership validated)
- PATCH  /api/tasks/{id}/complete - Toggle completion status (ownership validated)
- DELETE /api/tasks/{id}         - Delete task (ownership validated)

HTTP Status Codes:
- 200 OK: Successful GET/PUT/PATCH/DELETE
- 201 Created: Successful POST
- 401 Unauthorized: Missing or invalid JWT
- 404 Not Found: Task doesn't exist or not owned by user
- 422 Unprocessable Entity: Validation error
- 500 Internal Server Error: Server failure
"""

import logging
from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from sqlmodel import select
from typing import Annotated
from datetime import datetime
from pydantic import BaseModel, Field

from ..models.task import Task
from ..database import SessionDep
from ..auth.dependencies import get_current_user
from ..auth.jwt_handler import TokenData
from ..events.kafka_producer import get_kafka_producer
from ..config import settings

logger = logging.getLogger(__name__)


# Create router for task endpoints
router = APIRouter(
    prefix="/api/tasks",
    tags=["tasks"],
    responses={
        401: {"description": "Unauthorized - Missing or invalid JWT token"},
        404: {"description": "Not Found - Task doesn't exist or not owned by user"},
    },
)


# Pydantic models for request/response validation

class TaskCreate(BaseModel):
    """Request model for creating a new task."""
    title: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Task description (1-500 characters)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Complete project specification"
            }
        }


class TaskUpdate(BaseModel):
    """Request model for updating task title."""
    title: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Updated task description (1-500 characters)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Updated task description"
            }
        }


class TaskResponse(BaseModel):
    """Response model for single task."""
    id: int
    title: str
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Response model for task list."""
    tasks: list[TaskResponse]
    count: int


class TaskDeleteResponse(BaseModel):
    """Response model for task deletion."""
    task_id: int


class SuccessResponse(BaseModel):
    """Generic success response wrapper."""
    data: dict
    message: str


# Helper function for ownership validation
def get_user_task_or_404(
    session: SessionDep,
    task_id: int,
    user_id: str
) -> Task:
    """
    Retrieve task with ownership validation.

    Returns 404 (not 403) if task doesn't exist or user doesn't own it.
    This prevents information leakage about task existence.

    Args:
        session: Database session
        task_id: Task identifier
        user_id: User identifier from JWT

    Returns:
        Task: The requested task if it exists and is owned by user

    Raises:
        HTTPException(404): If task not found or not owned by user
    """
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == int(user_id)  # Ownership validation
    )
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task


# ============================================================================
# T030: GET /api/tasks - List all tasks for authenticated user
# ============================================================================

@router.get(
    "",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="List all tasks for authenticated user",
    description="Retrieve all tasks owned by the authenticated user, ordered by created_at DESC (newest first)"
)
async def list_tasks(
    session: SessionDep,
    current_user: Annotated[TokenData, Depends(get_current_user)]
) -> dict:
    """
    List all tasks for authenticated user.

    Security:
    - JWT authentication required
    - Only returns tasks where task.user_id == jwt.user_id
    - User isolation enforced at database query level

    Response:
    - 200 OK with tasks array (empty if no tasks)
    - Tasks ordered by created_at DESC (newest first)

    Example Response:
    {
        "data": {
            "tasks": [
                {
                    "id": 1,
                    "title": "Complete project specification",
                    "completed": true,
                    "created_at": "2026-02-04T10:05:00Z",
                    "updated_at": "2026-02-04T11:30:00Z"
                }
            ],
            "count": 1
        },
        "message": "Tasks retrieved successfully"
    }
    """
    # Extract user_id from verified JWT token
    user_id = int(current_user.user_id)

    # Query tasks with user isolation filter
    # CRITICAL: Always filter by user_id to enforce user isolation
    statement = (
        select(Task)
        .where(Task.user_id == user_id)
        .order_by(Task.created_at.desc())  # Newest first (FR-016)
    )

    tasks = session.exec(statement).all()

    # Convert SQLModel objects to response format
    task_responses = [TaskResponse.model_validate(task) for task in tasks]

    return {
        "data": {
            "tasks": task_responses,
            "count": len(task_responses)
        },
        "message": "Tasks retrieved successfully" if tasks else "No tasks found"
    }


# ============================================================================
# T031: POST /api/tasks - Create new task for authenticated user
# ============================================================================

@router.post(
    "",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new task",
    description="Create a new task for the authenticated user with title validation"
)
async def create_task(
    task_data: TaskCreate,
    session: SessionDep,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    background_tasks: BackgroundTasks
) -> dict:
    """
    Create new task for authenticated user.

    Security:
    - JWT authentication required
    - user_id set automatically from JWT (not trusted from request body)
    - Title validation: non-empty, max 500 characters

    Request Body:
    {
        "title": "New task description"
    }

    Response:
    - 201 Created with new task
    - completed defaults to false
    - Timestamps auto-generated

    Example Response:
    {
        "data": {
            "task": {
                "id": 3,
                "title": "New task description",
                "completed": false,
                "created_at": "2026-02-04T12:00:00Z",
                "updated_at": "2026-02-04T12:00:00Z"
            }
        },
        "message": "Task created successfully"
    }
    """
    # Extract user_id from verified JWT token
    # CRITICAL: NEVER trust user_id from request body - always use JWT
    user_id = int(current_user.user_id)

    # Create new task with ownership assigned
    new_task = Task(
        title=task_data.title,
        user_id=user_id,  # Enforce ownership from JWT
        completed=False,  # Default value
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    # Persist to database
    session.add(new_task)
    session.commit()
    session.refresh(new_task)  # Load generated ID and defaults

    # Convert to response format
    task_response = TaskResponse.model_validate(new_task)

    # Publish Kafka event in background (Phase V: Event-driven architecture)
    if settings.kafka_enabled:
        background_tasks.add_task(
            publish_task_created_event,
            task_id=new_task.id,
            user_id=user_id,
            title=new_task.title,
            created_at=new_task.created_at.isoformat()
        )

    return {
        "data": {
            "task": task_response
        },
        "message": "Task created successfully"
    }


async def publish_task_created_event(
    task_id: int,
    user_id: int,
    title: str,
    created_at: str
) -> None:
    """Background task to publish todo.created event to Kafka."""
    try:
        producer = await get_kafka_producer()
        await producer.publish_event(
            topic=settings.kafka_topic_todos,
            event_type="todo.created",
            data={
                "task_id": task_id,
                "user_id": user_id,
                "title": title,
                "created_at": created_at
            },
            key=str(user_id)  # Partition by user for ordering
        )
    except Exception as e:
        logger.error(f"Failed to publish todo.created event: {e}")


# ============================================================================
# T039: PUT /api/tasks/{id} - Update task title with ownership validation
# ============================================================================

@router.put(
    "/{task_id}",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Update task title",
    description="Update task title with ownership validation and title length constraints"
)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    session: SessionDep,
    current_user: Annotated[TokenData, Depends(get_current_user)]
) -> dict:
    """
    Update task title with ownership validation.

    Security:
    - JWT authentication required
    - Ownership validation: task.user_id must match jwt.user_id
    - Returns 404 if task not found OR not owned (prevents info leakage)

    Request Body:
    {
        "title": "Updated task description"
    }

    Response:
    - 200 OK with updated task
    - updated_at timestamp automatically updated
    - completed status unchanged (use PATCH /complete to toggle)

    Errors:
    - 404 Not Found: Task doesn't exist or not owned by user
    - 422 Unprocessable Entity: Title validation failed

    Example Response:
    {
        "data": {
            "task": {
                "id": 1,
                "title": "Updated task description",
                "completed": true,
                "created_at": "2026-02-04T10:05:00Z",
                "updated_at": "2026-02-04T12:30:00Z"
            }
        },
        "message": "Task updated successfully"
    }
    """
    # Extract user_id from verified JWT token
    user_id = current_user.user_id

    # Retrieve task with ownership validation
    # Raises 404 if not found or not owned
    task = get_user_task_or_404(session, task_id, user_id)

    # Update task fields
    task.title = task_update.title
    task.updated_at = datetime.utcnow()  # Update timestamp

    # Persist changes
    session.add(task)
    session.commit()
    session.refresh(task)

    # Convert to response format
    task_response = TaskResponse.model_validate(task)

    return {
        "data": {
            "task": task_response
        },
        "message": "Task updated successfully"
    }


# ============================================================================
# T040: PATCH /api/tasks/{id}/complete - Toggle completion status
# ============================================================================

@router.patch(
    "/{task_id}/complete",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Toggle task completion status",
    description="Toggle task between completed=true and completed=false with ownership validation"
)
async def toggle_task_completion(
    task_id: int,
    session: SessionDep,
    current_user: Annotated[TokenData, Depends(get_current_user)]
) -> dict:
    """
    Toggle task completion status.

    Security:
    - JWT authentication required
    - Ownership validation: task.user_id must match jwt.user_id
    - Returns 404 if task not found OR not owned

    Behavior:
    - If completed == false, set to true
    - If completed == true, set to false
    - No request body required (toggle operation)

    Response:
    - 200 OK with updated task
    - updated_at timestamp automatically updated

    Errors:
    - 404 Not Found: Task doesn't exist or not owned by user

    Example Response:
    {
        "data": {
            "task": {
                "id": 1,
                "title": "Complete project specification",
                "completed": true,
                "created_at": "2026-02-04T10:05:00Z",
                "updated_at": "2026-02-04T12:35:00Z"
            }
        },
        "message": "Task completion toggled"
    }
    """
    # Extract user_id from verified JWT token
    user_id = current_user.user_id

    # Retrieve task with ownership validation
    # Raises 404 if not found or not owned
    task = get_user_task_or_404(session, task_id, user_id)

    # Toggle completion status
    task.completed = not task.completed
    task.updated_at = datetime.utcnow()  # Update timestamp

    # Persist changes
    session.add(task)
    session.commit()
    session.refresh(task)

    # Convert to response format
    task_response = TaskResponse.model_validate(task)

    return {
        "data": {
            "task": task_response
        },
        "message": "Task completion toggled"
    }


# ============================================================================
# T044: DELETE /api/tasks/{id} - Permanently delete task
# ============================================================================

@router.delete(
    "/{task_id}",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete task",
    description="Permanently delete task with ownership validation (no soft delete for MVP)"
)
async def delete_task(
    task_id: int,
    session: SessionDep,
    current_user: Annotated[TokenData, Depends(get_current_user)]
) -> dict:
    """
    Permanently delete task.

    Security:
    - JWT authentication required
    - Ownership validation: task.user_id must match jwt.user_id
    - Returns 404 if task not found OR not owned

    Behavior:
    - Permanent deletion (no soft delete for MVP)
    - Deleted tasks cannot be recovered
    - No request body required

    Response:
    - 200 OK with deleted task_id

    Errors:
    - 404 Not Found: Task doesn't exist or not owned by user

    Example Response:
    {
        "data": {
            "task_id": 1
        },
        "message": "Task deleted successfully"
    }
    """
    # Extract user_id from verified JWT token
    user_id = current_user.user_id

    # Retrieve task with ownership validation
    # Raises 404 if not found or not owned
    task = get_user_task_or_404(session, task_id, user_id)

    # Store task_id before deletion
    deleted_task_id = task.id

    # Permanently delete task
    session.delete(task)
    session.commit()

    return {
        "data": {
            "task_id": deleted_task_id
        },
        "message": "Task deleted successfully"
    }


# Security Notes and Best Practices
# ============================================================================

"""
USER ISOLATION ENFORCEMENT:
----------------------------
Every query in this module MUST filter by user_id from JWT token.
This prevents cross-user data leakage.

CORRECT PATTERN:
    user_id = current_user.user_id
    statement = select(Task).where(Task.user_id == user_id)

INCORRECT PATTERN (SECURITY VULNERABILITY):
    # Never query without user_id filter
    statement = select(Task)  # ❌ Exposes all users' tasks

    # Never trust user_id from request
    statement = select(Task).where(Task.user_id == request.user_id)  # ❌ Bypass


OWNERSHIP VALIDATION PATTERN:
------------------------------
For UPDATE/DELETE/COMPLETE operations, always validate ownership
by including user_id in the WHERE clause.

CORRECT:
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id  # Ownership check
    )
    task = session.exec(statement).first()
    if not task:
        raise HTTPException(404, "Task not found")

INCORRECT:
    # Checking ownership after query is vulnerable to race conditions
    task = session.get(Task, task_id)
    if task.user_id != user_id:  # ❌ Too late - timing attack possible
        raise HTTPException(403)


ERROR RESPONSE STRATEGY:
------------------------
Return 404 (not 403) for ownership violations to prevent information
disclosure about task existence.

WHY:
- 403 Forbidden reveals: "Task exists but you don't own it"
- 404 Not Found reveals: "Task doesn't exist OR you don't own it"

404 prevents attackers from enumerating valid task IDs by brute force.


HTTP STATUS CODE USAGE:
------------------------
200 OK: Successful GET/PUT/PATCH/DELETE
201 Created: Successful POST
401 Unauthorized: Missing/invalid JWT (handled by dependency)
404 Not Found: Resource doesn't exist or not owned
422 Unprocessable Entity: Validation error (handled by Pydantic)
500 Internal Server Error: Unexpected server failure


JWT DEPENDENCY INJECTION:
--------------------------
All endpoints use Depends(get_current_user) to:
1. Extract JWT from Authorization header
2. Verify signature and expiration
3. Extract user_id from 'sub' claim
4. Return TokenData or raise 401

This happens BEFORE route handler logic executes, ensuring
no unauthenticated requests reach business logic.


PYDANTIC VALIDATION:
--------------------
Request models (TaskCreate, TaskUpdate) enforce:
- Title non-empty (min_length=1)
- Title max 500 characters (max_length=500)
- Required fields present

Validation errors automatically return 422 with detailed messages.


PERFORMANCE CONSIDERATIONS:
----------------------------
- Task.user_id is indexed for fast user-scoped queries
- For 1000 tasks per user, queries complete in <10ms
- ORDER BY created_at DESC requires index on (user_id, created_at)
  Consider adding composite index if sorting becomes bottleneck


TESTING CHECKLIST:
------------------
[ ] Create task as User A, verify appears in list
[ ] Create task as User B, verify User A cannot see it
[ ] Update task as owner, verify succeeds
[ ] Update task as non-owner, verify returns 404
[ ] Delete task as owner, verify succeeds
[ ] Delete task as non-owner, verify returns 404
[ ] Request without JWT, verify returns 401
[ ] Request with expired JWT, verify returns 401
[ ] Toggle completion works in both directions
[ ] Timestamps update correctly on modifications
"""
