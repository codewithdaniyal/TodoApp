"""
MCP-style tools for task management.

These tools provide the interface between the AI agent and the database.
All tools are stateless, validate user_id, and return JSON-serializable data.

SECURITY: All tools require user_id parameter and enforce user isolation.
"""

import json
from typing import Dict, List, Optional
from sqlmodel import Session, select
from ..models.task import Task
from ..database import engine


# =============================================================================
# MCP TOOL IMPLEMENTATIONS
# =============================================================================

def list_tasks(user_id: int) -> List[Dict]:
    """
    List all tasks for authenticated user.

    Args:
        user_id: Authenticated user ID from JWT token

    Returns:
        List of task dictionaries with id, title, completed, created_at

    Security:
        Queries are filtered by user_id to enforce user isolation
    """
    try:
        with Session(engine) as session:
            tasks = session.exec(
                select(Task).where(Task.user_id == user_id)
            ).all()

            return [
                {
                    "id": task.id,
                    "title": task.title,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat(),
                }
                for task in tasks
            ]
    except Exception as e:
        return {"error": f"Failed to list tasks: {str(e)}"}


def create_task(user_id: int, title: str) -> Dict:
    """
    Create new task for authenticated user.

    Args:
        user_id: Authenticated user ID from JWT token
        title: Task title/description

    Returns:
        Dict with created task details and success message

    Security:
        Task is created with user_id from JWT (cannot be spoofed)
    """
    try:
        with Session(engine) as session:
            task = Task(
                user_id=user_id,
                title=title,
                completed=False
            )
            session.add(task)
            session.commit()
            session.refresh(task)

            return {
                "id": task.id,
                "title": task.title,
                "completed": task.completed,
                "created_at": task.created_at.isoformat(),
                "message": f"Task '{title}' created successfully"
            }
    except Exception as e:
        return {"error": f"Failed to create task: {str(e)}"}


def update_task(
    user_id: int,
    task_id: int,
    title: Optional[str] = None,
    completed: Optional[bool] = None
) -> Dict:
    """
    Update existing task (ownership validated).

    Args:
        user_id: Authenticated user ID from JWT token
        task_id: ID of task to update
        title: New title (optional)
        completed: New completion status (optional)

    Returns:
        Dict with updated task details or error

    Security:
        Verifies task belongs to user before updating (404 if not owned)
    """
    try:
        with Session(engine) as session:
            # Query with user_id filter for security
            task = session.exec(
                select(Task)
                .where(Task.id == task_id)
                .where(Task.user_id == user_id)
            ).first()

            if not task:
                return {"error": "Task not found or not owned by user"}

            # Update fields
            if title is not None:
                task.title = title
            if completed is not None:
                task.completed = completed

            session.add(task)
            session.commit()
            session.refresh(task)

            return {
                "id": task.id,
                "title": task.title,
                "completed": task.completed,
                "message": "Task updated successfully"
            }
    except Exception as e:
        return {"error": f"Failed to update task: {str(e)}"}


def delete_task(user_id: int, task_id: int) -> Dict:
    """
    Delete task (ownership validated).

    Args:
        user_id: Authenticated user ID from JWT token
        task_id: ID of task to delete

    Returns:
        Dict with success message or error

    Security:
        Verifies task belongs to user before deleting (404 if not owned)
    """
    try:
        with Session(engine) as session:
            # Query with user_id filter for security
            task = session.exec(
                select(Task)
                .where(Task.id == task_id)
                .where(Task.user_id == user_id)
            ).first()

            if not task:
                return {"error": "Task not found or not owned by user"}

            session.delete(task)
            session.commit()

            return {"message": f"Task '{task.title}' deleted successfully"}
    except Exception as e:
        return {"error": f"Failed to delete task: {str(e)}"}


def get_task(user_id: int, task_id: int) -> Dict:
    """
    Get specific task details (ownership validated).

    Args:
        user_id: Authenticated user ID from JWT token
        task_id: ID of task to retrieve

    Returns:
        Dict with task details or error

    Security:
        Verifies task belongs to user (404 if not owned)
    """
    try:
        with Session(engine) as session:
            # Query with user_id filter for security
            task = session.exec(
                select(Task)
                .where(Task.id == task_id)
                .where(Task.user_id == user_id)
            ).first()

            if not task:
                return {"error": "Task not found or not owned by user"}

            return {
                "id": task.id,
                "title": task.title,
                "completed": task.completed,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat()
            }
    except Exception as e:
        return {"error": f"Failed to get task: {str(e)}"}


# =============================================================================
# TOOL DEFINITIONS FOR OPENAI ASSISTANTS API
# =============================================================================

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List all tasks for the authenticated user",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "integer",  # Changed from "string" to "integer"
                        "description": "The authenticated user's ID"
                    }
                },
                "required": ["user_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Create a new task for the authenticated user",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "integer",  # Changed from "string" to "integer"
                        "description": "The authenticated user's ID"
                    },
                    "title": {
                        "type": "string",
                        "description": "The task title or description"
                    }
                },
                "required": ["user_id", "title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update an existing task (title or completion status)",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "integer",  # Changed from "string" to "integer"
                        "description": "The authenticated user's ID"
                    },
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to update"
                    },
                    "title": {
                        "type": "string",
                        "description": "New task title (optional)"
                    },
                    "completed": {
                        "type": "boolean",
                        "description": "New completion status (optional)"
                    }
                },
                "required": ["user_id", "task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "integer",  # Changed from "string" to "integer"
                        "description": "The authenticated user's ID"
                    },
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to delete"
                    }
                },
                "required": ["user_id", "task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_task",
            "description": "Get details of a specific task",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "integer",  # Changed from "string" to "integer"
                        "description": "The authenticated user's ID"
                    },
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to retrieve"
                    }
                },
                "required": ["user_id", "task_id"]
            }
        }
    }
]


# =============================================================================
# TOOL DISPATCHER
# =============================================================================

# Map tool names to functions
TOOL_FUNCTIONS = {
    "list_tasks": list_tasks,
    "create_task": create_task,
    "update_task": update_task,
    "delete_task": delete_task,
    "get_task": get_task
}


def execute_tool(tool_name: str, arguments: Dict) -> Dict:
    """
    Execute MCP tool by name with given arguments.

    Args:
        tool_name: Name of the tool to execute
        arguments: Dict of arguments for the tool

    Returns:
        Tool execution result as JSON-serializable dict

    Security:
        All tools validate user_id parameter
    """
    if tool_name not in TOOL_FUNCTIONS:
        return {"error": f"Unknown tool: {tool_name}"}

    try:
        result = TOOL_FUNCTIONS[tool_name](**arguments)
        return result
    except Exception as e:
        return {"error": f"Tool execution failed: {str(e)}"}
