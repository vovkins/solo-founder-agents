"""Developer (Reviewer) agent for code review."""

from crewai import Agent

from src.crews.base import LLMProvider
from src.agents.factory import agent_factory
from src.tools import get_readonly_artifact_tools

# System prompt for Developer Reviewer
def create_reviewer_agent() -> Agent:
    """Create and return the Reviewer agent using AgentFactory.

    Returns:
        Configured Agent instance for reviewer role
    """
    return agent_factory.create_agent("reviewer")


# Pre-configured Reviewer agent instance
reviewer_agent = create_reviewer_agent()