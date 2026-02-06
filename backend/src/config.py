"""
Configuration management using Pydantic Settings.
Loads environment variables for database, JWT, and CORS configuration.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Required environment variables:
    - DATABASE_URL: PostgreSQL connection string (must include ?sslmode=require for Neon)
    - BETTER_AUTH_SECRET: JWT signing secret (32+ characters, shared with Next.js)
    - CORS_ORIGINS: Comma-separated list of allowed origins
    - OPENAI_API_KEY: OpenAI API key for Assistants API
    - OPENAI_ASSISTANT_ID: Pre-created OpenAI assistant ID
    """

    # Database Configuration
    database_url: str

    # JWT Configuration
    better_auth_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_hours: int = 24

    # CORS Configuration
    cors_origins: str = "http://localhost:3000"

    # Application Settings
    app_name: str = "Todo API"
    debug: bool = True

    # OpenAI Configuration (Phase III)
    openai_api_key: str = ""
    openai_assistant_id: str = ""
    
    # OpenRouter Configuration (Alternative to OpenAI)
    openrouter_api_key: str = ""

    # Kafka Configuration (Phase V)
    kafka_enabled: bool = True
    kafka_bootstrap_servers: str = "kafka:9092"
    kafka_topic_todos: str = "todos"

    class Config:
        env_file = ".env"
        case_sensitive = False

    def get_cors_origins_list(self) -> List[str]:
        """Parse comma-separated CORS origins into list.
        If '*' is in the list, allow all origins for development.
        """
        origins = [origin.strip() for origin in self.cors_origins.split(",")]
        if "*" in origins:
            return ["*"]
        return origins


# Global settings instance
settings = Settings()
