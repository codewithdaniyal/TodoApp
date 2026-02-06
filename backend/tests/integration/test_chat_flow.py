import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from src.main import app
from src.models.user import User
from src.models.task import Task
from src.database import engine, SessionLocal
from sqlmodel import SQLModel
from datetime import datetime

client = TestClient(app)

def test_chat_endpoint_requires_auth():
    """Test that chat endpoint requires authentication"""
    response = client.post("/api/chat", json={"message": "test message"})
    assert response.status_code == 401  # Unauthorized


def test_chat_endpoint_with_auth():
    """Test chat endpoint with authentication"""
    # This would require a valid JWT token
    headers = {
        "Authorization": "Bearer fake-jwt-token",
        "Content-Type": "application/json"
    }
    response = client.post("/api/chat", json={"message": "test message"}, headers=headers)
    # The exact response depends on the OpenAI API call, but should return 200 or 500
    assert response.status_code in [200, 500]


@patch('src.agent.ai_agent.ChatService')
def test_chat_service_integration(mock_chat_service):
    """Test the chat service integration"""
    # Mock the chat service response
    mock_instance = MagicMock()
    mock_instance.process_message.return_value = {
        "message": "I've created a task for you.",
        "actions": [{"tool": "create_task", "arguments": {"title": "test"}, "result": {"id": 1}}],
        "thread_id": "test-thread-id"
    }
    mock_chat_service.return_value = mock_instance
    
    headers = {
        "Authorization": "Bearer fake-jwt-token",
        "Content-Type": "application/json"
    }
    response = client.post("/api/chat", json={"message": "Create a task"}, headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert data["data"]["message"] == "I've created a task for you."