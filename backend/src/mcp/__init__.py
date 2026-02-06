"""
MCP (Model Context Protocol) tools for AI agent.

This module provides MCP-style tools that the AI agent uses to interact
with the task management system. All tools are stateless and validate
user_id to enforce user isolation.
"""

from .tools import (
    list_tasks,
    create_task,
    update_task,
    delete_task,
    get_task,
    execute_tool,
    TOOL_DEFINITIONS
)

__all__ = [
    "list_tasks",
    "create_task",
    "update_task",
    "delete_task",
    "get_task",
    "execute_tool",
    "TOOL_DEFINITIONS"
]
