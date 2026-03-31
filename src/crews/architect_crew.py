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
    from src.agents import architect_agent
    from src.tasks import (
        create_analyze_requirements_task,
        create_design_architecture_task,
        create_system_design_task,
        create_standards_task,
    )

    # Create Architect tasks
    analyze_requirements = create_analyze_requirements_task(
        "data/artifacts/docs/prd.md",
        "",
    )
    design_architecture = create_design_architecture_task("{{requirements_summary}}")
    create_system_design = create_system_design_task(
        "data/artifacts/docs/prd.md",
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


def run_architect_crew() -> dict:
    """Run the Architect crew and return results.

    Returns:
        Dictionary with results and outputs
    """
    crew = create_architect_crew()
    result = crew.kickoff()

    return {
        "status": "completed",
        "result": str(result),
        "artifacts": {
            "system_design": "data/artifacts/docs/system-design.md",
            "standards": "data/artifacts/docs/standards.md",
        },
    }
