"""CrewAI base configuration and utilities."""

from crewai import LLM
from config.settings import settings


def create_llm(model: str) -> LLM:
    """Create an LLM instance configured for OpenRouter."""
    return LLM(
        model=f"openrouter/{model}",
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
    )


# Cache for LLM instances (model_name -> LLM)
_llm_cache: dict = {}


def _get_or_create_llm(model_name: str) -> LLM:
    """Get cached LLM or create a new one."""
    if model_name not in _llm_cache:
        _llm_cache[model_name] = create_llm(model_name)
    return _llm_cache[model_name]


class LLMProvider:
    """Provider for LLM instances by agent role (cached)."""

    @staticmethod
    def get_pm_llm() -> LLM:
        return _get_or_create_llm(settings.llm_pm)

    @staticmethod
    def get_analyst_llm() -> LLM:
        return _get_or_create_llm(settings.llm_analyst)

    @staticmethod
    def get_architect_llm() -> LLM:
        return _get_or_create_llm(settings.llm_architect)

    @staticmethod
    def get_designer_llm() -> LLM:
        return _get_or_create_llm(settings.llm_designer)

    @staticmethod
    def get_developer_llm() -> LLM:
        return _get_or_create_llm(settings.llm_developer)

    @staticmethod
    def get_reviewer_llm() -> LLM:
        return _get_or_create_llm(settings.llm_reviewer)

    @staticmethod
    def get_qa_llm() -> LLM:
        return _get_or_create_llm(settings.llm_qa)

    @staticmethod
    def get_tech_writer_llm() -> LLM:
        return _get_or_create_llm(settings.llm_tech_writer)
