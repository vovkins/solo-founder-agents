"""Agents package for CrewAI agents."""

from .pm import create_pm_agent, pm_agent, PM_SYSTEM_PROMPT
from .analyst import create_analyst_agent, analyst_agent, ANALYST_SYSTEM_PROMPT
from .architect import create_architect_agent, architect_agent, ARCHITECT_SYSTEM_PROMPT

__all__ = [
    # PM Agent
    "create_pm_agent",
    "pm_agent",
    "PM_SYSTEM_PROMPT",
    # Analyst Agent
    "create_analyst_agent",
    "analyst_agent",
    "ANALYST_SYSTEM_PROMPT",
    # Architect Agent
    "create_architect_agent",
    "architect_agent",
    "ARCHITECT_SYSTEM_PROMPT",
]
