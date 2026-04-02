"""Tech Writer crew for documentation tasks."""

from crewai import Crew, Process


def create_tech_writer_crew(
    project_name: str = "Project",
    project_description: str = "",
    verbose: bool = True,
) -> Crew:
    """Create a crew with only the Tech Writer agent."""
    from src.agents import tech_writer_agent
    from src.tasks import (
        create_readme_task,
        create_changelog_task,
    )

    update_readme = create_readme_task(project_name, project_description)
    changelog = create_changelog_task("{{changes_summary}}", "1.0.0")

    return Crew(
        agents=[tech_writer_agent],
        tasks=[update_readme, changelog],
        process=Process.sequential,
        verbose=verbose,
    )


def run_tech_writer_crew(
    project_name: str = "Project",
    project_description: str = "",
) -> dict:
    """Run the tech writer crew."""
    from src.tools.file_permissions import set_current_role
    set_current_role("tech_writer")

    crew = create_tech_writer_crew(project_name, project_description)
    result = crew.kickoff()

    return {
        "status": "completed",
        "result": str(result),
    }
