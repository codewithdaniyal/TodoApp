import pytest
from unittest.mock import patch, MagicMock, create_autospec
from src.mcp.tools import (
    list_tasks, create_task, update_task, delete_task, get_task, execute_tool
)
from src.models.task import Task
from datetime import datetime


def test_list_tasks():
    """Test listing tasks for a user"""
    with patch('src.mcp.tools.Session') as mock_session_class:
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        
        # Mock tasks
        mock_task1 = Task(id=1, title="Task 1", completed=False, user_id=123, created_at=datetime.now())
        mock_task2 = Task(id=2, title="Task 2", completed=True, user_id=123, created_at=datetime.now())
        
        mock_query_result = [mock_task1, mock_task2]
        mock_session.exec.return_value.all.return_value = mock_query_result
        
        result = list_tasks(user_id="123")
        
        # Verify the query was called with correct filter
        mock_session.exec.assert_called_once()
        # Check that the result contains the expected tasks
        assert len(result) == 2
        assert result[0]["title"] == "Task 1"
        assert result[1]["title"] == "Task 2"


def test_create_task():
    """Test creating a new task"""
    with patch('src.mcp.tools.Session') as mock_session_class:
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        
        result = create_task(user_id="123", title="New Task")
        
        # Verify the task was added to the session
        assert mock_session.add.called
        assert mock_session.commit.called
        assert result["title"] == "New Task"
        assert result["completed"] == False


def test_update_task():
    """Test updating an existing task"""
    with patch('src.mcp.tools.Session') as mock_session_class:
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        
        # Mock task query result
        mock_task = Task(id=1, title="Old Title", completed=False, user_id=123, created_at=datetime.now())
        mock_session.exec.return_value.first.return_value = mock_task
        
        result = update_task(user_id="123", task_id=1, title="New Title", completed=True)
        
        # Verify the task was updated
        assert mock_task.title == "New Title"
        assert mock_task.completed == True
        assert mock_session.commit.called
        assert result["title"] == "New Title"
        assert result["completed"] == True


def test_delete_task():
    """Test deleting a task"""
    with patch('src.mcp.tools.Session') as mock_session_class:
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        
        # Mock task query result
        mock_task = Task(id=1, title="Task to Delete", completed=False, user_id=123, created_at=datetime.now())
        mock_session.exec.return_value.first.return_value = mock_task
        
        result = delete_task(user_id="123", task_id=1)
        
        # Verify the task was deleted
        mock_session.delete.assert_called_once_with(mock_task)
        assert mock_session.commit.called
        assert "deleted successfully" in result["message"]


def test_get_task():
    """Test getting a specific task"""
    with patch('src.mcp.tools.Session') as mock_session_class:
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        
        # Mock task query result
        mock_task = Task(id=1, title="Test Task", completed=False, user_id=123, created_at=datetime.now())
        mock_session.exec.return_value.first.return_value = mock_task
        
        result = get_task(user_id="123", task_id=1)
        
        assert result["id"] == 1
        assert result["title"] == "Test Task"
        assert result["completed"] == False


def test_execute_tool():
    """Test executing a tool by name"""
    with patch('src.mcp.tools.Session'):
        # Test valid tool
        result = execute_tool("create_task", {"user_id": "123", "title": "Test Task"})
        assert "id" in result
        assert "title" in result
        
        # Test invalid tool
        result = execute_tool("invalid_tool", {})
        assert "error" in result
        assert "Unknown tool" in result["error"]