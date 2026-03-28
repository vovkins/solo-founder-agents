"""Configuration management using pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # API Keys
    openrouter_api_key: str
    github_token: str
    github_repo: str
    telegram_bot_token: str = ""

    # LLM Models per Agent (OpenRouter format)
    llm_pm: str = "openai/gpt-4o"
    llm_analyst: str = "openai/gpt-4o"
    llm_architect: str = "openai/gpt-4o"
    llm_designer: str = "openai/gpt-4o"
    llm_developer: str = "anthropic/claude-sonnet"
    llm_reviewer: str = "openai/gpt-4o"
    llm_qa: str = "openai/gpt-4o"
    llm_tech_writer: str = "openai/gpt-4o"

    # OpenRouter Base URL
    openrouter_base_url: str = "https://openrouter.ai/api/v1"


# Global settings instance
settings = Settings()
