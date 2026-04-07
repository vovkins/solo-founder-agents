"""PM crew for requirements and PRD creation."""

from typing import Optional
from src.crews.types import CrewResult
from crewai import Crew, Process


def create_pm_crew(
    founder_vision: str,
    verbose: bool = True,
) -> Crew:
    """Create a crew for PM tasks (requirements + PRD + backlog).

    Args:
        founder_vision: Initial product vision from founder
        verbose: Whether to show detailed output

    Returns:
        Configured Crew instance
    """
    from src.agents import get_pm_agent
    pm_agent = get_pm_agent()
    from src.tasks import (
        create_collect_requirements_task,
        create_prd_task,
        create_backlog_task,
        create_prioritize_backlog_task,
    )

    # Create PM tasks
    collect_requirements = create_collect_requirements_task(founder_vision)
    create_prd = create_prd_task("{{requirements_output}}")
    generate_backlog = create_backlog_task("{{prd_output}}")
    prioritize_backlog = create_prioritize_backlog_task(["{{issue_urls}}"])

    return Crew(
        agents=[pm_agent],
        tasks=[
            collect_requirements,
            create_prd,
            generate_backlog,
            prioritize_backlog,
        ],
        process=Process.sequential,
        verbose=verbose,
    )


def run_pm_crew(founder_vision: str) -> CrewResult:
    """Run the PM crew and return results."""
    import logging
    from src.tools.file_permissions import set_current_role

    logger = logging.getLogger(__name__)
    set_current_role("pm")

    try:
        crew = create_pm_crew(founder_vision)
        result = crew.kickoff()
        return {
            "status": "completed",
            "result": str(result),
            "artifacts": {"prd": "docs/requirements/prd.md"},
        }
    except Exception as e:
        logger.error(f"PM crew failed: {e}")
        return {"status": "error", "error": str(e)}
