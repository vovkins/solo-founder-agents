from src.crews.types import CrewResult
"""Architect crew for system design and architecture."""

from typing import Optional
from crewai import Crew, Process


def create_architect_crew(
    verbose: bool = True,
) -> Crew:
    """Create a crew for Architect tasks (architecture + system design).

    Args:
        verbose: Whether to show detailed output

    Returns:
        Configured Crew instance
    """
    from src.agents import get_architect_agent
    architect_agent = get_architect_agent()
    from src.tasks import (
        create_analyze_requirements_task,
        create_design_architecture_task,
        create_system_design_task,
        create_standards_task,
    )

    # Create Architect tasks
    analyze_requirements = create_analyze_requirements_task(
        "docs/requirements/prd.md",
        "",
    )
    design_architecture = create_design_architecture_task("{{requirements_summary}}")
    create_system_design = create_system_design_task(
        "docs/requirements/prd.md",
        "{{architecture_output}}",
    )
    create_standards = create_standards_task("{{architecture_output}}")

    return Crew(
        agents=[architect_agent],
        tasks=[
            analyze_requirements,
            design_architecture,
            create_system_design,
            create_standards,
        ],
        process=Process.sequential,
        verbose=verbose,
    )


def run_architect_crew() -> CrewResult:
    """Run the Architect crew and return results."""
    import logging
    from src.tools.file_permissions import set_current_role

    logger = logging.getLogger(__name__)
    set_current_role("architect")

    try:
        crew = create_architect_crew()
        result = crew.kickoff()
        return {
            "status": "completed",
            "result": result.raw if hasattr(result, 'raw') else str(result),
            "artifacts": {
                "system_design": "docs/design/system-design.md",
                "standards": "docs/design/standards.md",
            },
        }
    except Exception as e:
        logger.error(f"Architect crew failed: {e}")
        return {"status": "error", "error": str(e)}
