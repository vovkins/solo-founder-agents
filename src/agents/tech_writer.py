"""Technical Writer agent for documentation."""

from crewai import Agent

from src.crews.base import LLMProvider
from src.agents.factory import agent_factory
from src.tools import get_artifact_tools

# System prompt for Tech Writer
def create_tech_writer_agent() -> Agent:
    """Create and return the Tech Writer agent using AgentFactory.

    Returns:
        Configured Agent instance for tech_writer role
    """
    return agent_factory.create_agent("tech_writer")


# Pre-configured Tech Writer agent instance
tech_writer_agent = create_tech_writer_agent()