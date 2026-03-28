"""Agents package for CrewAI agents."""

from .pm import create_pm_agent, pm_agent, PM_SYSTEM_PROMPT
from .analyst import create_analyst_agent, analyst_agent, ANALYST_SYSTEM_PROMPT
from .architect import create_architect_agent, architect_agent, ARCHITECT_SYSTEM_PROMPT
from .designer import create_designer_agent, designer_agent, DESIGNER_SYSTEM_PROMPT
from .developer import create_developer_agent, developer_agent, DEVELOPER_SYSTEM_PROMPT
from .reviewer import create_reviewer_agent, reviewer_agent, REVIEWER_SYSTEM_PROMPT
from .qa import create_qa_agent, qa_agent, QA_SYSTEM_PROMPT
from .tech_writer import create_tech_writer_agent, tech_writer_agent, TECH_WRITER_SYSTEM_PROMPT

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
    # Designer Agent
    "create_designer_agent",
    "designer_agent",
    "DESIGNER_SYSTEM_PROMPT",
    # Developer Agent
    "create_developer_agent",
    "developer_agent",
    "DEVELOPER_SYSTEM_PROMPT",
    # Reviewer Agent
    "create_reviewer_agent",
    "reviewer_agent",
    "REVIEWER_SYSTEM_PROMPT",
    # QA Agent
    "create_qa_agent",
    "qa_agent",
    "QA_SYSTEM_PROMPT",
    # Tech Writer Agent
    "create_tech_writer_agent",
    "tech_writer_agent",
    "TECH_WRITER_SYSTEM_PROMPT",
]
