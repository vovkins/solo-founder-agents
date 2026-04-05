"""Lazy agent initialization with caching."""

_agent_cache: dict = {}


def get_pm_agent():
    """Get PM agent (cached)."""
    if "pm" not in _agent_cache:
        from .pm import create_pm_agent
        _agent_cache["pm"] = create_pm_agent()
    return _agent_cache["pm"]


def get_analyst_agent():
    """Get Analyst agent (cached)."""
    if "analyst" not in _agent_cache:
        from .analyst import create_analyst_agent
        _agent_cache["analyst"] = create_analyst_agent()
    return _agent_cache["analyst"]


def get_architect_agent():
    """Get Architect agent (cached)."""
    if "architect" not in _agent_cache:
        from .architect import create_architect_agent
        _agent_cache["architect"] = create_architect_agent()
    return _agent_cache["architect"]


def get_designer_agent():
    """Get Designer agent (cached)."""
    if "designer" not in _agent_cache:
        from .designer import create_designer_agent
        _agent_cache["designer"] = create_designer_agent()
    return _agent_cache["designer"]


def get_developer_agent():
    """Get Developer agent (cached)."""
    if "developer" not in _agent_cache:
        from .developer import create_developer_agent
        _agent_cache["developer"] = create_developer_agent()
    return _agent_cache["developer"]


def get_reviewer_agent():
    """Get Reviewer agent (cached)."""
    if "reviewer" not in _agent_cache:
        from .reviewer import create_reviewer_agent
        _agent_cache["reviewer"] = create_reviewer_agent()
    return _agent_cache["reviewer"]


def get_qa_agent():
    """Get QA agent (cached)."""
    if "qa" not in _agent_cache:
        from .qa import create_qa_agent
        _agent_cache["qa"] = create_qa_agent()
    return _agent_cache["qa"]


def get_tech_writer_agent():
    """Get Tech Writer agent (cached)."""
    if "tech_writer" not in _agent_cache:
        from .tech_writer import create_tech_writer_agent
        _agent_cache["tech_writer"] = create_tech_writer_agent()
    return _agent_cache["tech_writer"]
