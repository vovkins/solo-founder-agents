"""CrewAI crews and utilities."""

from .base import create_llm, LLMProvider

# Lazy imports for crews to avoid circular dependency
def create_core_crew(*args, **kwargs):
    from .core_crew import create_core_crew as _create_core_crew
    return _create_core_crew(*args, **kwargs)

def run_core_crew(*args, **kwargs):
    from .core_crew import run_core_crew as _run_core_crew
    return _run_core_crew(*args, **kwargs)

def create_dev_crew(*args, **kwargs):
    from .dev_crew import create_dev_crew as _create_dev_crew
    return _create_dev_crew(*args, **kwargs)

def run_dev_crew(*args, **kwargs):
    from .dev_crew import run_dev_crew as _run_dev_crew
    return _run_dev_crew(*args, **kwargs)

def create_review_cycle_crew(*args, **kwargs):
    from .dev_crew import create_review_cycle_crew as _create_review_cycle_crew
    return _create_review_cycle_crew(*args, **kwargs)

def create_qa_cycle_crew(*args, **kwargs):
    from .dev_crew import create_qa_cycle_crew as _create_qa_cycle_crew
    return _create_qa_cycle_crew(*args, **kwargs)

# New separate crews to avoid context overflow
def create_pm_crew(*args, **kwargs):
    from .pm_crew import create_pm_crew as _create_pm_crew
    return _create_pm_crew(*args, **kwargs)

def run_pm_crew(*args, **kwargs):
    from .pm_crew import run_pm_crew as _run_pm_crew
    return _run_pm_crew(*args, **kwargs)

def create_analyst_crew(*args, **kwargs):
    from .analyst_crew import create_analyst_crew as _create_analyst_crew
    return _create_analyst_crew(*args, **kwargs)

def run_analyst_crew(*args, **kwargs):
    from .analyst_crew import run_analyst_crew as _run_analyst_crew
    return _run_analyst_crew(*args, **kwargs)

def create_architect_crew(*args, **kwargs):
    from .architect_crew import create_architect_crew as _create_architect_crew
    return _create_architect_crew(*args, **kwargs)

def run_architect_crew(*args, **kwargs):
    from .architect_crew import run_architect_crew as _run_architect_crew
    return _run_architect_crew(*args, **kwargs)

__all__ = [
    "create_llm",
    "LLMProvider",
    "create_core_crew",
    "run_core_crew",
    "create_dev_crew",
    "run_dev_crew",
    "create_review_cycle_crew",
    "create_qa_cycle_crew",
    "create_pm_crew",
    "run_pm_crew",
    "create_analyst_crew",
    "run_analyst_crew",
    "create_architect_crew",
    "run_architect_crew",
]
