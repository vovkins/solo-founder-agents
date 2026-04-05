"""UI/UX Designer agent for creating design system and UI specifications."""

from crewai import Agent

from src.crews.base import LLMProvider
from src.agents.factory import agent_factory
from src.tools import get_artifact_tools, get_artifact_manager, ArtifactType

# System prompt for Designer
def create_designer_agent() -> Agent:
    """Create and return the Designer agent using AgentFactory.

    Returns:
        Configured Agent instance for designer role
    """
    return agent_factory.create_agent("designer")


# Pre-configured Designer agent instance
designer_agent = create_designer_agent()