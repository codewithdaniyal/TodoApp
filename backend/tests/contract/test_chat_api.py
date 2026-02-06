import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from src.main import app
from src.auth.dependencies import get_current_user
from src.auth.jwt_handler import TokenData

client = TestClient(app)

def override_get_current_user():
    return TokenData(user_id="123", email="test@example.com")

app.dependency_overrides[get_current_user] = override_get_current_user


def test_chat_endpoint_valid_request():
    """Test chat endpoint with valid request"""
    with patch('src.agent.ai_agent.ChatService') as mock_service:
        mock_instance = MagicMock()
        mock_instance.process_message.return_value = {
            "message": "I've processed your request.",
            "actions": [],
            "thread_id": "test-thread-id"
        }
        mock_service.return_value = mock_instance
        
        response = client.post("/api/chat", json={"message": "Create a task to buy groceries"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["message"] == "I've processed your request."
        assert data["data"]["thread_id"] == "test-thread-id"


def test_chat_endpoint_empty_message():
    """Test chat endpoint with empty message"""
    response = client.post("/api/chat", json={"message": ""})
    
    # Should return 422 for validation error
    assert response.status_code == 422


def test_chat_endpoint_missing_message_field():
    """Test chat endpoint without message field"""
    response = client.post("/api/chat", json={})
    
    # Should return 422 for validation error
    assert response.status_code == 422


def test_chat_endpoint_long_message():
    """Test chat endpoint with very long message"""
    long_message = "A" * 4001  # Exceeds 4000 character limit
    response = client.post("/api/chat", json={"message": long_message})
    
    # Should return 422 for validation error
    assert response.status_code == 422


def test_chat_endpoint_with_mocked_agent_failure():
    """Test chat endpoint when agent fails"""
    with patch('src.agent.ai_agent.ChatService') as mock_service:
        mock_instance = MagicMock()
        mock_instance.process_message.return_value = {
            "error": "Agent execution failed",
            "thread_id": "test-thread-id"
        }
        mock_service.return_value = mock_instance
        
        response = client.post("/api/chat", json={"message": "Test message"})
        
        # Should return 500 for server error
        assert response.status_code == 500