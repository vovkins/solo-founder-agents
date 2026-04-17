"""Tech Writer crew for documentation tasks."""

from crewai import Crew, Process

from src.crews.types import CrewResult


def create_tech_writer_crew(verbose: bool = True) -> Crew:
    """Create a crew with only the Tech Writer agent."""
    from src.agents import get_tech_writer_agent
    tech_writer_agent = get_tech_writer_agent()
    from src.tasks import (
        create_readme_task,
        create_changelog_task,
    )

    update_readme = create_readme_task()
    changelog = create_changelog_task()

    return Crew(
        agents=[tech_writer_agent],
        tasks=[update_readme, changelog],
        process=Process.sequential,
        verbose=verbose,
    )


def run_tech_writer_crew() -> CrewResult:
    """Run the tech writer crew."""
    import logging
    from src.tools.file_permissions import set_current_role

    logger = logging.getLogger(__name__)
    set_current_role("tech_writer")

    try:
        crew = create_tech_writer_crew()
        result = crew.kickoff()
        return {"status": "completed", "result": str(result)}
    except Exception as e:
        logger.error(f"Tech Writer crew failed: {e}")
        return {"status": "error", "error": str(e)}
