"""QA Engineer agent for testing and quality assurance."""

from crewai import Agent

from src.crews.base import LLMProvider
from src.agents.factory import agent_factory
from src.tools import get_artifact_tools

# System prompt for QA Engineer
def create_qa_agent() -> Agent:
    """Create and return the Qa agent using AgentFactory.

    Returns:
        Configured Agent instance for qa role
    """
    return agent_factory.create_agent("qa")


# Pre-configured QA agent instance
qa_agent = create_qa_agent()