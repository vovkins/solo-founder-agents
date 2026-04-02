"""Core crew for PM, Analyst, and Architect agents."""

from typing import Optional
from crewai import Crew, Process


def create_core_crew(
    founder_vision: str,
    verbose: bool = True,
) -> Crew:
    """Create a crew for core product development (PM + Analyst + Architect).

    Args:
        founder_vision: Initial product vision from founder
        verbose: Whether to show detailed output

    Returns:
        Configured Crew instance
    """
    # Lazy imports to avoid circular dependency
    from src.agents import pm_agent, analyst_agent, architect_agent
    from src.tasks import (
        create_collect_requirements_task,
        create_prd_task,
        create_backlog_task,
        create_prioritize_backlog_task,
        create_analyze_prd_task,
        create_decompose_features_task,
        create_task_specs_task,
        create_dependency_map_task,
        create_analyze_requirements_task,
        create_design_architecture_task,
        create_system_design_task,
        create_standards_task,
    )

    # Create tasks
    collect_requirements = create_collect_requirements_task(founder_vision)
    create_prd = create_prd_task("{{requirements_output}}")
    generate_backlog = create_backlog_task("{{prd_output}}")
    prioritize_backlog = create_prioritize_backlog_task(["{{issue_urls}}"])

    analyze_prd = create_analyze_prd_task("data/artifacts/docs/prd.md")
    decompose_features = create_decompose_features_task("{{features_output}}")
    create_task_specs = create_task_specs_task("{{tasks_output}}")
    map_dependencies = create_dependency_map_task(["{{task_urls}}"])

    analyze_requirements = create_analyze_requirements_task(
        "data/artifacts/docs/prd.md",
        "{{tasks_summary}}",
    )
    design_architecture = create_design_architecture_task("{{requirements_summary}}")
    create_system_design = create_system_design_task(
        "data/artifacts/docs/prd.md",
        "{{architecture_output}}",
    )
    create_standards = create_standards_task("{{architecture_output}}")

    return Crew(
        agents=[pm_agent, analyst_agent, architect_agent],
        tasks=[
            # PM tasks
            collect_requirements,
            create_prd,
            generate_backlog,
            prioritize_backlog,
            # Analyst tasks
            analyze_prd,
            decompose_features,
            create_task_specs,
            map_dependencies,
            # Architect tasks
            analyze_requirements,
            design_architecture,
            create_system_design,
            create_standards,
        ],
        process=Process.sequential,
        verbose=verbose,
    )


def run_core_crew(founder_vision: str) -> dict:
    """Run the core crew (PM + Analyst + Architect) and return results."""
    from src.tools.file_permissions import set_current_role
    set_current_role("core_crew")  # Combined PM + Analyst + Architect permissions
    
    crew = create_core_crew(founder_vision)
    result = crew.kickoff()

    return {
        "status": "completed",
        "result": str(result),
        "artifacts": {
            "prd": "data/artifacts/docs/prd.md",
            "system_design": "data/artifacts/docs/system-design.md",
            "standards": "data/artifacts/docs/standards.md",
        },
    }
