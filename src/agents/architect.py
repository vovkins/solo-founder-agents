"""Software Architect agent for system design and ADRs."""

from crewai import Agent

from src.crews.base import LLMProvider
from src.agents.factory import agent_factory
from src.tools import get_artifact_tools

# System prompt for Architect
def create_architect_agent() -> Agent:
    """Create and return the Architect agent using AgentFactory.

    Returns:
        Configured Agent instance for architect role
    """
    return agent_factory.create_agent("architect")


# Pre-configured Architect agent instance
architect_agent = create_architect_agent()