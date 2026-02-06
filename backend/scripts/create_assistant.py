"""
One-time script to create OpenAI Assistant for Task Management.

Run this script once to create the assistant and save the ID to .env file.

Usage:
    cd backend
    python scripts/create_assistant.py

The script will:
1. Create an OpenAI Assistant with task management tools
2. Print the assistant ID
3. Remind you to add it to .env as OPENAI_ASSISTANT_ID
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from openai import OpenAI
from dotenv import load_dotenv
from src.agent.system_prompt import SYSTEM_PROMPT

# Load environment variables
load_dotenv()

def create_assistant():
    """Create OpenAI Assistant with task management tools."""

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ ERROR: OPENAI_API_KEY not found in environment")
        print("Please add OPENAI_API_KEY to backend/.env file")
        sys.exit(1)

    print("🤖 Creating Task Management Assistant...")
    print()

    client = OpenAI(api_key=api_key)

    # Define MCP tools for task management
    tools = [
        {
            "type": "function",
            "function": {
                "name": "list_tasks",
                "description": "List all tasks for the authenticated user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
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
                            "type": "string",
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
                            "type": "string",
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
                            "type": "string",
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
                            "type": "string",
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

    # Use the system prompt from the dedicated module
    instructions = SYSTEM_PROMPT

    try:
        assistant = client.beta.assistants.create(
            name="Task Management Agent",
            instructions=instructions,
            model="gpt-4-turbo-preview",
            tools=tools
        )

        print("✅ Assistant created successfully!")
        print()
        print("=" * 60)
        print(f"ASSISTANT ID: {assistant.id}")
        print("=" * 60)
        print()
        print("📝 Next steps:")
        print("1. Copy the assistant ID above")
        print("2. Add to backend/.env file:")
        print(f"   OPENAI_ASSISTANT_ID={assistant.id}")
        print()
        print("3. Restart your backend server to load the new configuration")
        print()

        return assistant.id

    except Exception as e:
        print(f"❌ ERROR creating assistant: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_assistant()