"""
Application settings using Pydantic BaseSettings
"""

from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # API Settings
    API_TITLE: str = "AI Chatbot API"
    API_DESCRIPTION: str = (
        "API for interacting with an AI chatbot through WebSocket connections"
    )
    API_VERSION: str = "1.0.0"

    # Database Settings
    DATABASE_HOST: str
    DATABASE_PORT: int = 5432
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_NAME: str

    # CORS Settings
    CORS_ORIGINS: List[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    @property
    def DATABASE_URL(self) -> str:
        """Get the database URL"""
        return f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"

    class Config:
        """Configuration for the settings"""
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
