"""
FastAPI REST API endpoint for AI chat agent.

Implements POST /api/chat for natural language task management.

SECURITY: JWT authentication required, user_id extracted from token.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from ..auth.dependencies import get_current_user
from ..auth.jwt_handler import TokenData
from ..agent.ai_agent import ChatService
from ..models.message import Message
from ..database import SessionDep
import json


# Create router for chat endpoints
router = APIRouter(
    prefix="/api/chat",
    tags=["chat"],
    responses={
        401: {"description": "Unauthorized - Missing or invalid JWT token"},
        422: {"description": "Validation Error - Invalid request format"},
        500: {"description": "Server Error - OpenAI API or internal failure"}
    }
)


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class ChatRequest(BaseModel):
    """Request model for chat message."""
    message: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="User's chat message (natural language)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Create a task to buy groceries"
            }
        }


class ToolCallAction(BaseModel):
    """Model for tool call action in response."""
    tool: str
    arguments: Dict
    result: Dict


class ChatResponseData(BaseModel):
    """Data model for chat response."""
    message: str
    actions: List[ToolCallAction]
    thread_id: str


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    data: ChatResponseData


# =============================================================================
# CHAT ENDPOINT
# =============================================================================

@router.post("", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def send_chat_message(
    request: ChatRequest,
    session: SessionDep,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Process chat message and return AI agent response.

    Flow:
        1. Extract user_id from JWT token
        2. Load existing thread_id from database (if exists)
        3. Store user message in database
        4. Execute AI agent with OpenAI Assistants API
        5. Store assistant response in database
        6. Return response to frontend

    Args:
        request: ChatRequest with user message
        session: Database session
        current_user: Authenticated user from JWT

    Returns:
        ChatResponse with agent message, tool actions, thread_id

    Raises:
        HTTPException 401: If JWT invalid
        HTTPException 422: If message validation fails
        HTTPException 500: If agent execution fails

    Security:
        - JWT authentication required (via get_current_user dependency)
        - user_id extracted from JWT token (cannot be spoofed)
        - All MCP tool calls automatically inject user_id
        - Messages filtered by user_id (user isolation)
    """
    user_id = current_user.user_id

    try:
        # Load existing thread_id from most recent message (if exists)
        from sqlmodel import select, desc
        latest_message = session.exec(
            select(Message)
            .where(Message.user_id == user_id)
            .order_by(desc(Message.created_at))
            .limit(1)
        ).first()

        thread_id = latest_message.thread_id if latest_message else None

        # Store user message BEFORE agent execution
        user_message = Message(
            user_id=user_id,
            thread_id=thread_id or "pending",  # Temp value, updated after agent creates thread
            role="user",
            content=request.message
        )
        session.add(user_message)
        session.commit()

        # Execute AI agent
        chat_service = ChatService()
        agent_response = chat_service.process_message(
            user_id=user_id,
            message=request.message,
            thread_id=thread_id
        )

        # Check for errors
        if "error" in agent_response:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=agent_response["error"]
            )

        # Update user message with correct thread_id if it was newly created
        if thread_id is None:
            user_message.thread_id = agent_response["thread_id"]
            session.add(user_message)
            session.commit()

        # Store assistant response AFTER agent execution
        assistant_message = Message(
            user_id=user_id,
            thread_id=agent_response["thread_id"],
            role="assistant",
            content=agent_response["message"],
            tool_calls=json.dumps(agent_response["actions"]) if agent_response["actions"] else None
        )
        session.add(assistant_message)
        session.commit()

        # Format response
        return ChatResponse(
            data=ChatResponseData(
                message=agent_response["message"],
                actions=[
                    ToolCallAction(**action)
                    for action in agent_response["actions"]
                ],
                thread_id=agent_response["thread_id"]
            )
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat processing failed: {str(e)}"
        )
