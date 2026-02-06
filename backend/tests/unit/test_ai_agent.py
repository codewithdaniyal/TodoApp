import pytest
from unittest.mock import patch, MagicMock
from src.agent.ai_agent import ChatService


@patch('src.config.settings')
def test_chat_service_initialization(mock_settings):
    """Test ChatService initialization"""
    mock_settings.openai_api_key = "fake-key"
    mock_settings.openai_assistant_id = "fake-assistant-id"
    
    service = ChatService()
    
    assert service.client is not None
    assert service.assistant_id == "fake-assistant-id"


@patch('src.config.settings')
@patch('openai.OpenAI')
def test_process_message_success(mock_openai_client, mock_settings):
    """Test successful message processing"""
    # Setup mocks
    mock_settings.openai_api_key = "fake-key"
    mock_settings.openai_assistant_id = "fake-assistant-id"
    
    mock_client_instance = MagicMock()
    mock_openai_client.return_value = mock_client_instance
    
    mock_thread = MagicMock()
    mock_thread.id = "test-thread-id"
    mock_client_instance.beta.threads.create.return_value = mock_thread
    
    mock_run = MagicMock()
    mock_run.status = "completed"
    mock_run.id = "run-id"
    
    mock_message = MagicMock()
    mock_message.content = [MagicMock()]
    mock_message.content[0].text = MagicMock()
    mock_message.content[0].text.value = "Test response"
    
    mock_messages_list = MagicMock()
    mock_messages_list.data = [mock_message]
    
    mock_client_instance.beta.threads.runs.create.return_value = mock_run
    mock_client_instance.beta.threads.runs.retrieve.return_value = mock_run
    mock_client_instance.beta.threads.messages.list.return_value = mock_messages_list
    
    # Execute
    service = ChatService()
    result = service.process_message(user_id="user-123", message="test message")
    
    # Assert
    assert result["message"] == "Test response"
    assert result["thread_id"] == "test-thread-id"


@patch('src.config.settings')
@patch('openai.OpenAI')
def test_process_message_with_tool_calls(mock_openai_client, mock_settings):
    """Test message processing with tool calls"""
    # Setup mocks
    mock_settings.openai_api_key = "fake-key"
    mock_settings.openai_assistant_id = "fake-assistant-id"
    
    mock_client_instance = MagicMock()
    mock_openai_client.return_value = mock_client_instance
    
    mock_thread = MagicMock()
    mock_thread.id = "test-thread-id"
    mock_client_instance.beta.threads.create.return_value = mock_thread
    
    # Mock run that requires action
    mock_run_incomplete = MagicMock()
    mock_run_incomplete.status = "requires_action"
    mock_run_incomplete.id = "run-id"
    
    mock_run_complete = MagicMock()
    mock_run_complete.status = "completed"
    mock_run_complete.id = "run-id"
    
    # Mock tool call
    mock_tool_call = MagicMock()
    mock_tool_call.id = "call-id"
    mock_tool_call.function.name = "create_task"
    mock_tool_call.function.arguments = '{"title": "test task"}'
    
    mock_required_action = MagicMock()
    mock_required_action.submit_tool_outputs.tool_calls = [mock_tool_call]
    
    mock_run_incomplete.required_action = mock_required_action
    
    mock_message = MagicMock()
    mock_message.content = [MagicMock()]
    mock_message.content[0].text = MagicMock()
    mock_message.content[0].text.value = "Task created successfully"
    
    mock_messages_list = MagicMock()
    mock_messages_list.data = [mock_message]
    
    # Setup sequence of calls
    call_count = 0
    def run_retrieve_side_effect(*args, **kwargs):
        nonlocal call_count
        if call_count == 0:
            call_count += 1
            return mock_run_incomplete
        else:
            return mock_run_complete
    
    mock_client_instance.beta.threads.runs.create.return_value = mock_run_incomplete
    mock_client_instance.beta.threads.runs.retrieve.side_effect = run_retrieve_side_effect
    mock_client_instance.beta.threads.messages.list.return_value = mock_messages_list
    mock_client_instance.beta.threads.runs.submit_tool_outputs.return_value = mock_run_complete
    
    # Execute
    service = ChatService()
    result = service.process_message(user_id="user-123", message="create a task")
    
    # Assert
    assert result["message"] == "Task created successfully"
    assert result["thread_id"] == "test-thread-id"