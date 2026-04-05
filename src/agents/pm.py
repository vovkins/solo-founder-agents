"""Product Manager agent for collecting requirements and creating PRD."""

from crewai import Agent

from src.crews.base import LLMProvider
from src.agents.factory import agent_factory
from src.tools import get_artifact_tools
from src.tools.github_tools import (
    create_github_issue_tool,
    list_open_issues_tool,
)


def create_pm_agent() -> Agent:
    """Create and return the Pm agent using AgentFactory.

    Returns:
        Configured Agent instance for pm role
    """
    return agent_factory.create_agent("pm")


# Pre-configured PM agent instance
pm_agent = create_pm_agent()
