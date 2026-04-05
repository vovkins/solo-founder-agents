"""Developer (Coder) agent for implementing features and writing code."""

from crewai import Agent

from src.crews.base import LLMProvider
from src.agents.factory import agent_factory
from src.tools import get_artifact_tools, get_github_tools

# System prompt for Developer Coder
def create_developer_agent() -> Agent:
    """Create and return the Developer agent using AgentFactory.

    Returns:
        Configured Agent instance for developer role
    """
    return agent_factory.create_agent("developer")


# Pre-configured Developer agent instance
developer_agent = create_developer_agent()