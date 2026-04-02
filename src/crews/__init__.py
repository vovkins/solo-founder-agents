"""CrewAI crews and utilities."""

from .base import create_llm, LLMProvider

# Lazy imports for crews to avoid circular dependency

# Individual role crews (each crew has ONE agent with correct role)
def create_pm_crew(*args, **kwargs):
    from .pm_crew import create_pm_crew as _f
    return _f(*args, **kwargs)

def run_pm_crew(*args, **kwargs):
    from .pm_crew import run_pm_crew as _f
    return _f(*args, **kwargs)

def create_analyst_crew(*args, **kwargs):
    from .analyst_crew import create_analyst_crew as _f
    return _f(*args, **kwargs)

def run_analyst_crew(*args, **kwargs):
    from .analyst_crew import run_analyst_crew as _f
    return _f(*args, **kwargs)

def create_architect_crew(*args, **kwargs):
    from .architect_crew import create_architect_crew as _f
    return _f(*args, **kwargs)

def run_architect_crew(*args, **kwargs):
    from .architect_crew import run_architect_crew as _f
    return _f(*args, **kwargs)

def create_designer_crew(*args, **kwargs):
    from .designer_crew import create_designer_crew as _f
    return _f(*args, **kwargs)

def run_designer_crew(*args, **kwargs):
    from .designer_crew import run_designer_crew as _f
    return _f(*args, **kwargs)

def create_developer_crew(*args, **kwargs):
    from .developer_crew import create_developer_crew as _f
    return _f(*args, **kwargs)

def run_developer_crew(*args, **kwargs):
    from .developer_crew import run_developer_crew as _f
    return _f(*args, **kwargs)

def create_reviewer_crew(*args, **kwargs):
    from .reviewer_crew import create_reviewer_crew as _f
    return _f(*args, **kwargs)

def run_reviewer_crew(*args, **kwargs):
    from .reviewer_crew import run_reviewer_crew as _f
    return _f(*args, **kwargs)

def create_qa_crew(*args, **kwargs):
    from .qa_crew import create_qa_crew as _f
    return _f(*args, **kwargs)

def run_qa_crew(*args, **kwargs):
    from .qa_crew import run_qa_crew as _f
    return _f(*args, **kwargs)

def create_tech_writer_crew(*args, **kwargs):
    from .tech_writer_crew import create_tech_writer_crew as _f
    return _f(*args, **kwargs)

def run_tech_writer_crew(*args, **kwargs):
    from .tech_writer_crew import run_tech_writer_crew as _f
    return _f(*args, **kwargs)

# Legacy crews (kept for backward compatibility)
def create_core_crew(*args, **kwargs):
    from .core_crew import create_core_crew as _f
    return _f(*args, **kwargs)

def run_core_crew(*args, **kwargs):
    from .core_crew import run_core_crew as _f
    return _f(*args, **kwargs)

def create_dev_crew(*args, **kwargs):
    from .dev_crew import create_dev_crew as _f
    return _f(*args, **kwargs)

def run_dev_crew(*args, **kwargs):
    from .dev_crew import run_dev_crew as _f
    return _f(*args, **kwargs)

def create_review_cycle_crew(*args, **kwargs):
    from .dev_crew import create_review_cycle_crew as _f
    return _f(*args, **kwargs)

def create_qa_cycle_crew(*args, **kwargs):
    from .dev_crew import create_qa_cycle_crew as _f
    return _f(*args, **kwargs)


__all__ = [
    "create_llm",
    "LLMProvider",
    # Individual crews
    "create_pm_crew", "run_pm_crew",
    "create_analyst_crew", "run_analyst_crew",
    "create_architect_crew", "run_architect_crew",
    "create_designer_crew", "run_designer_crew",
    "create_developer_crew", "run_developer_crew",
    "create_reviewer_crew", "run_reviewer_crew",
    "create_qa_crew", "run_qa_crew",
    "create_tech_writer_crew", "run_tech_writer_crew",
    # Legacy
    "create_core_crew", "run_core_crew",
    "create_dev_crew", "run_dev_crew",
    "create_review_cycle_crew",
    "create_qa_cycle_crew",
]
