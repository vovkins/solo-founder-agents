from src.crews.types import CrewResult
"""Analyst crew for epic decomposition and task specs."""

from typing import Optional
from crewai import Crew, Process


def create_analyst_crew(
    backlog_path: str = "docs/requirements/backlog.md",
    verbose: bool = True,
) -> Crew:
    """Create a crew for Analyst tasks (epic decomposition + task specs).

    Args:
        backlog_path: Path to the PM's epic-level backlog
        verbose: Whether to show detailed output

    Returns:
        Configured Crew instance
    """
    from src.agents import get_analyst_agent
    analyst_agent = get_analyst_agent()
    from src.tasks import (
        create_analyze_backlog_task,
        create_decompose_epics_task,
        create_task_specs_task,
        create_dependency_map_task,
    )

    # Create Analyst tasks
    analyze_backlog = create_analyze_backlog_task(backlog_path)
    decompose_epics = create_decompose_epics_task("{{analysis_output}}")
    create_task_specs = create_task_specs_task("{{tasks_output}}")
    map_dependencies = create_dependency_map_task(["{{task_urls}}"])

    return Crew(
        agents=[analyst_agent],
        tasks=[
            analyze_backlog,
            decompose_epics,
            create_task_specs,
            map_dependencies,
        ],
        process=Process.sequential,
        verbose=verbose,
    )


def run_analyst_crew(
    backlog_path: str = "docs/requirements/backlog.md",
) -> CrewResult:
    """Run the Analyst crew and return results."""
    import logging
    from src.tools.file_permissions import set_current_role

    logger = logging.getLogger(__name__)
    set_current_role("analyst")

    try:
        crew = create_analyst_crew(backlog_path)
        result = crew.kickoff()
        return {
            "status": "completed",
            "result": result.raw if hasattr(result, 'raw') else str(result),
            "artifacts": {"task_specs": "docs/requirements/task-specs.md"},
        }
    except Exception as e:
        logger.error(f"Analyst crew failed: {e}")
        return {"status": "error", "error": str(e)}
