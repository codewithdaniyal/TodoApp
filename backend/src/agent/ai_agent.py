"""
ChatService class using OpenAI Assistants API.

Provides stateless AI agent execution with MCP tool integration.
Each request reconstructs context from database and executes agent.

SECURITY: user_id is injected from JWT token into all tool calls.
"""

import json
import time
from typing import Dict, List, Optional
from openai import OpenAI
from ..config import settings
from ..mcp.tools import execute_tool
from .system_prompt import SYSTEM_PROMPT
from ..models.message import Message


class ChatService:
    """
    Stateless chat service using OpenAI Assistants API.

    Each request:
    1. Gets or creates thread_id
    2. Adds user message to thread
    3. Runs assistant with tool execution loop
    4. Returns assistant response with tool calls

    Architecture:
    - Stateless: No in-memory state between requests
    - Thread-based: OpenAI stores conversation context
    - Tool-driven: All task operations via MCP tools
    - User-scoped: user_id injected into all tool calls
    """

    def __init__(self):
        """Initialize OpenAI client and load assistant ID."""
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.assistant_id = settings.openai_assistant_id

    def process_message(
        self,
        user_id: str,
        message: str,
        thread_id: Optional[str] = None
    ) -> Dict:
        """
        Process chat message (stateless operation).

        Args:
            user_id: Authenticated user ID from JWT
            message: User's message text
            thread_id: Existing thread ID or None for new thread

        Returns:
            Dict with:
            - message: Assistant's natural language response
            - actions: List of tool calls executed
            - thread_id: OpenAI thread ID for conversation

        Process:
            1. Get or create thread
            2. Add user message to thread
            3. Run assistant with user_id injection
            4. Poll and handle tool calls
            5. Extract assistant response
        """
        try:
            # 1. Get or create thread
            if thread_id is None:
                thread = self.client.beta.threads.create()
                thread_id = thread.id

            # 2. Add user message to thread
            self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=message
            )

            # 3. Run assistant
            run = self.client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=self.assistant_id
            )

            # 4. Poll and handle tool calls
            tool_calls_executed = []
            max_iterations = 10  # Prevent infinite loops
            iteration = 0

            while run.status not in ["completed", "failed", "cancelled", "expired"]:
                iteration += 1
                if iteration > max_iterations:
                    return {
                        "error": "Agent exceeded maximum iterations",
                        "thread_id": thread_id
                    }

                # Wait before polling
                time.sleep(1)

                # Get current run status
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
                )

                # Handle tool calls
                if run.status == "requires_action":
                    tool_outputs = []

                    for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                        # Parse tool arguments
                        try:
                            args = json.loads(tool_call.function.arguments)
                        except json.JSONDecodeError:
                            args = {}

                        # CRITICAL: Inject user_id from JWT (cannot be spoofed)
                        # Convert string user_id from JWT to integer for database operations
                        args["user_id"] = int(user_id)

                        # Execute MCP tool
                        result = execute_tool(tool_call.function.name, args)

                        # Record tool call for audit
                        tool_calls_executed.append({
                            "tool": tool_call.function.name,
                            "arguments": args,
                            "result": result
                        })

                        # Submit tool output to OpenAI
                        tool_outputs.append({
                            "tool_call_id": tool_call.id,
                            "output": json.dumps(result)
                        })

                    # Submit all tool outputs
                    run = self.client.beta.threads.runs.submit_tool_outputs(
                        thread_id=thread_id,
                        run_id=run.id,
                        tool_outputs=tool_outputs
                    )

            # 5. Extract assistant response
            if run.status == "completed":
                messages = self.client.beta.threads.messages.list(
                    thread_id=thread_id,
                    order="desc",
                    limit=1
                )

                if messages.data:
                    assistant_message = messages.data[0].content[0].text.value

                    return {
                        "message": assistant_message,
                        "actions": tool_calls_executed,
                        "thread_id": thread_id
                    }

            # Handle failure cases
            return {
                "error": f"Agent execution failed with status: {run.status}",
                "thread_id": thread_id
            }

        except Exception as e:
            return {
                "error": f"Chat service error: {str(e)}",
                "thread_id": thread_id if thread_id else None
            }