"""Settings configuration for solo-founder-agents."""

from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str = ""
    AUTHORIZED_USERS: list[int] = []
    
    # GitHub
    GITHUB_TOKEN: str = ""
    GITHUB_REPO: str = ""
    GITHUB_DEFAULT_BRANCH: str = "main"
    
    # OpenRouter
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    
    # LLM Models
    LLM_PM: str = "openrouter/auto"
    LLM_ANALYST: str = "openrouter/auto"
    LLM_ARCHITECT: str = "openrouter/auto"
    LLM_DESIGNER: str = "openrouter/auto"
    LLM_DEVELOPER: str = "openrouter/auto"
    LLM_REVIEWER: str = "openrouter/auto"
    LLM_QA: str = "openrouter/auto"
    LLM_TECH_WRITER: str = "openrouter/auto"
    
    @field_validator("AUTHORIZED_USERS", mode="before")
    @classmethod
    def parse_authorized_users(cls, v):
        """Parse AUTHORIZED_USERS from string to list."""
        if isinstance(v, str):
            return [int(x.strip()) for x in v.split(",") if x.strip()]
        return v
    
    model_config = {"env_file": ".env", "case_sensitive": False}


settings = Settings()
