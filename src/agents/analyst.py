"""Business Analyst agent for decomposing features into tasks."""

from crewai import Agent

from src.crews.base import LLMProvider
from src.agents.factory import agent_factory
from src.tools import get_artifact_tools
from src.tools.github_tools import create_github_issue_tool

# System prompt for Analyst
def create_analyst_agent() -> Agent:
    """Create and return the Analyst agent using AgentFactory.

    Returns:
        Configured Agent instance for analyst role
    """
    return agent_factory.create_agent("analyst")


# Pre-configured Analyst agent instance
analyst_agent = create_analyst_agent()