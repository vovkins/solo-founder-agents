"""Agents package for CrewAI agents (lazy initialization)."""

from .factory import agent_factory

# Export factory functions and system prompts (no agent instances!)
from .pm import create_pm_agent
from .analyst import create_analyst_agent
from .architect import create_architect_agent
from .designer import create_designer_agent
from .developer import create_developer_agent
from .reviewer import create_reviewer_agent
from .qa import create_qa_agent
from .tech_writer import create_tech_writer_agent

# Lazy getters with caching
from ._agent_cache import (
    get_pm_agent,
    get_analyst_agent,
    get_architect_agent,
    get_designer_agent,
    get_developer_agent,
    get_reviewer_agent,
    get_qa_agent,
    get_tech_writer_agent,
)

__all__ = [
    "agent_factory",
    # Factory functions
    "create_pm_agent", "create_analyst_agent", "create_architect_agent",
    "create_designer_agent", "create_developer_agent", "create_reviewer_agent",
    "create_qa_agent", "create_tech_writer_agent",
    # Lazy getters
    "get_pm_agent", "get_analyst_agent", "get_architect_agent",
    "get_designer_agent", "get_developer_agent", "get_reviewer_agent",
    "get_qa_agent", "get_tech_writer_agent",
]
