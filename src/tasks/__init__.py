"""Tasks package for CrewAI agents."""

from .pm_tasks import (
    create_collect_requirements_task,
    create_prd_task,
    create_backlog_task,
    create_prioritize_backlog_task,
)
from .analyst_tasks import (
    create_analyze_prd_task,
    create_decompose_features_task,
    create_task_specs_task,
    create_dependency_map_task,
    create_sprint_recommendations_task,
)
from .architect_tasks import (
    create_analyze_requirements_task,
    create_design_architecture_task,
    create_adr_task,
    create_system_design_task,
    create_standards_task,
    create_api_spec_task,
)

__all__ = [
    # PM Tasks
    "create_collect_requirements_task",
    "create_prd_task",
    "create_backlog_task",
    "create_prioritize_backlog_task",
    # Analyst Tasks
    "create_analyze_prd_task",
    "create_decompose_features_task",
    "create_task_specs_task",
    "create_dependency_map_task",
    "create_sprint_recommendations_task",
    # Architect Tasks
    "create_analyze_requirements_task",
    "create_design_architecture_task",
    "create_adr_task",
    "create_system_design_task",
    "create_standards_task",
    "create_api_spec_task",
]
