"""Agents package for CrewAI agents (lazy initialization)."""

# Export factory functions and system prompts (no agent instances!)
from .pm import create_pm_agent, PM_SYSTEM_PROMPT
from .analyst import create_analyst_agent, ANALYST_SYSTEM_PROMPT
from .architect import create_architect_agent, ARCHITECT_SYSTEM_PROMPT
from .designer import create_designer_agent, DESIGNER_SYSTEM_PROMPT
from .developer import create_developer_agent, DEVELOPER_SYSTEM_PROMPT
from .reviewer import create_reviewer_agent, REVIEWER_SYSTEM_PROMPT
from .qa import create_qa_agent, QA_SYSTEM_PROMPT
from .tech_writer import create_tech_writer_agent, TECH_WRITER_SYSTEM_PROMPT

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
    # Factory functions
    "create_pm_agent", "create_analyst_agent", "create_architect_agent",
    "create_designer_agent", "create_developer_agent", "create_reviewer_agent",
    "create_qa_agent", "create_tech_writer_agent",
    # Lazy getters
    "get_pm_agent", "get_analyst_agent", "get_architect_agent",
    "get_designer_agent", "get_developer_agent", "get_reviewer_agent",
    "get_qa_agent", "get_tech_writer_agent",
    # System prompts
    "PM_SYSTEM_PROMPT", "ANALYST_SYSTEM_PROMPT", "ARCHITECT_SYSTEM_PROMPT",
    "DESIGNER_SYSTEM_PROMPT", "DEVELOPER_SYSTEM_PROMPT", "REVIEWER_SYSTEM_PROMPT",
    "QA_SYSTEM_PROMPT", "TECH_WRITER_SYSTEM_PROMPT",
]
