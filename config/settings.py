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
    # All roles use z-ai/glm-5, except Reviewer uses different model
    llm_pm: str = "z-ai/glm-5"
    llm_analyst: str = "z-ai/glm-5"
    llm_architect: str = "z-ai/glm-5"
    llm_designer: str = "z-ai/glm-5"
    llm_developer: str = "z-ai/glm-5"
    llm_reviewer: str = "openai/gpt-5.1-codex-mini"
    llm_qa: str = "z-ai/glm-5"
    llm_tech_writer: str = "z-ai/glm-5"

    # OpenRouter Base URL
    openrouter_base_url: str = "https://openrouter.ai/api/v1"


# Global settings instance
settings = Settings()
