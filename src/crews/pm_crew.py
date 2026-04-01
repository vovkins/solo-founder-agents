"""PM crew for requirements and PRD creation."""

from typing import Optional
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
    from src.agents import pm_agent
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


def run_pm_crew(founder_vision: str) -> dict:
    """Run the PM crew and return results.

    Args:
        founder_vision: Initial product vision from founder

    Returns:
        Dictionary with results and outputs
    """
    from src.tools.artifact_tools import set_current_role
    
    # Set role context for file permissions
    set_current_role("pm")
    
    crew = create_pm_crew(founder_vision)
    result = crew.kickoff()

    return {
        "status": "completed",
        "result": str(result),
        "artifacts": {
            "prd": "data/artifacts/docs/prd.md",
        },
    }
