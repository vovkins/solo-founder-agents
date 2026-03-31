"""Analyst crew for feature decomposition and task specs."""

from typing import Optional
from crewai import Crew, Process


def create_analyst_crew(
    verbose: bool = True,
) -> Crew:
    """Create a crew for Analyst tasks (feature decomposition + task specs).

    Args:
        verbose: Whether to show detailed output

    Returns:
        Configured Crew instance
    """
    from src.agents import analyst_agent
    from src.tasks import (
        create_analyze_prd_task,
        create_decompose_features_task,
        create_task_specs_task,
        create_dependency_map_task,
    )

    # Create Analyst tasks
    analyze_prd = create_analyze_prd_task("data/artifacts/docs/prd.md")
    decompose_features = create_decompose_features_task("{{features_output}}")
    create_task_specs = create_task_specs_task("{{tasks_output}}")
    map_dependencies = create_dependency_map_task(["{{task_urls}}"])

    return Crew(
        agents=[analyst_agent],
        tasks=[
            analyze_prd,
            decompose_features,
            create_task_specs,
            map_dependencies,
        ],
        process=Process.sequential,
        verbose=verbose,
    )


def run_analyst_crew() -> dict:
    """Run the Analyst crew and return results.

    Returns:
        Dictionary with results and outputs
    """
    crew = create_analyst_crew()
    result = crew.kickoff()

    return {
        "status": "completed",
        "result": str(result),
        "artifacts": {
            "task_specs": "data/artifacts/docs/task-specs.md",
        },
    }
