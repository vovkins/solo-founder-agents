"""CrewAI base configuration and utilities."""

from crewai import LLM
from config.settings import settings


def create_llm(model: str) -> LLM:
    """Create an LLM instance configured for OpenRouter.

    Args:
        model: Model name in OpenRouter format (e.g., 'openai/gpt-4o')

    Returns:
        Configured LLM instance
    """
    return LLM(
        model=f"openrouter/{model}",
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
    )


class LLMProvider:
    """Provider for LLM instances by agent role."""

    @staticmethod
    def get_pm_llm() -> LLM:
        """Get LLM for Product Manager agent."""
        return create_llm(settings.llm_pm)

    @staticmethod
    def get_analyst_llm() -> LLM:
        """Get LLM for Analyst agent."""
        return create_llm(settings.llm_analyst)

    @staticmethod
    def get_architect_llm() -> LLM:
        """Get LLM for Architect agent."""
        return create_llm(settings.llm_architect)

    @staticmethod
    def get_designer_llm() -> LLM:
        """Get LLM for Designer agent."""
        return create_llm(settings.llm_designer)

    @staticmethod
    def get_developer_llm() -> LLM:
        """Get LLM for Developer (Coder) agent."""
        return create_llm(settings.llm_developer)

    @staticmethod
    def get_reviewer_llm() -> LLM:
        """Get LLM for Developer (Reviewer) agent."""
        return create_llm(settings.llm_reviewer)

    @staticmethod
    def get_qa_llm() -> LLM:
        """Get LLM for QA Engineer agent."""
        return create_llm(settings.llm_qa)

    @staticmethod
    def get_tech_writer_llm() -> LLM:
        """Get LLM for Tech Writer agent."""
        return create_llm(settings.llm_tech_writer)
