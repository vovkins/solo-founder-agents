"""Settings configuration for solo-founder-agents."""

from typing import Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Telegram Bot
    telegram_bot_token: str = Field(default="", alias="TELEGRAM_BOT_TOKEN")
    authorized_users: list[int] = Field(default_factory=list, alias="AUTHORIZED_USERS")
    
    # GitHub
    github_token: str = Field(default="", alias="GITHUB_TOKEN")
    github_repo: str = Field(default="", alias="GITHUB_REPO")
    github_default_branch: str = Field(default="main", alias="GITHUB_DEFAULT_BRANCH")
    
    # OpenRouter
    openrouter_api_key: str = Field(default="", alias="OPENROUTER_API_KEY")
    openrouter_base_url: str = Field(default="https://openrouter.ai/api/v1", alias="OPENROUTER_BASE_URL")
    
    # LLM Models
    llm_pm: str = Field(default="openrouter/auto", alias="LLM_PM")
    llm_analyst: str = Field(default="openrouter/auto", alias="LLM_ANALYST")
    llm_architect: str = Field(default="openrouter/auto", alias="LLM_ARCHITECT")
    llm_designer: str = Field(default="openrouter/auto", alias="LLM_DESIGNER")
    llm_developer: str = Field(default="openrouter/auto", alias="LLM_DEVELOPER")
    llm_reviewer: str = Field(default="openrouter/auto", alias="LLM_REVIEWER")
    llm_qa: str = Field(default="openrouter/auto", alias="LLM_QA")
    llm_tech_writer: str = Field(default="openrouter/auto", alias="LLM_TECH_WRITER")
    
    @field_validator("authorized_users", mode="before")
    @classmethod
    def parse_authorized_users(cls, v: Union[str, int, list]) -> list:
        """Parse AUTHORIZED_USERS from string/int to list."""
        if isinstance(v, int):
            return [v]
        if isinstance(v, str):
            return [int(x.strip()) for x in v.split(",") if x.strip()]
        return v
    
    model_config = {
        "env_file": ".env",
        "populate_by_name": True,
        "extra": "ignore",
    }


settings = Settings()
