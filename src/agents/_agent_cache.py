"""Lazy agent initialization with caching.

Architecture improvement A: Now uses AgentCache with TTL and LRU eviction.
"""

from .agent_cache import agent_cache


def get_pm_agent():
    """Get PM agent (cached with TTL)."""
    from .pm import create_pm_agent
    return agent_cache.get_or_create("pm", create_pm_agent)


def get_analyst_agent():
    """Get Analyst agent (cached with TTL)."""
    from .analyst import create_analyst_agent
    return agent_cache.get_or_create("analyst", create_analyst_agent)


def get_architect_agent():
    """Get Architect agent (cached with TTL)."""
    from .architect import create_architect_agent
    return agent_cache.get_or_create("architect", create_architect_agent)


def get_designer_agent():
    """Get Designer agent (cached with TTL)."""
    from .designer import create_designer_agent
    return agent_cache.get_or_create("designer", create_designer_agent)


def get_developer_agent():
    """Get Developer agent (cached with TTL)."""
    from .developer import create_developer_agent
    return agent_cache.get_or_create("developer", create_developer_agent)


def get_reviewer_agent():
    """Get Reviewer agent (cached with TTL)."""
    from .reviewer import create_reviewer_agent
    return agent_cache.get_or_create("reviewer", create_reviewer_agent)


def get_qa_agent():
    """Get QA agent (cached with TTL)."""
    from .qa import create_qa_agent
    return agent_cache.get_or_create("qa", create_qa_agent)


def get_tech_writer_agent():
    """Get Tech Writer agent (cached with TTL)."""
    from .tech_writer import create_tech_writer_agent
    return agent_cache.get_or_create("tech_writer", create_tech_writer_agent)


def get_agent_cache_stats():
    """Get agent cache statistics."""
    return agent_cache.stats()


def clear_agent_cache():
    """Clear all cached agents."""
    agent_cache.clear()
