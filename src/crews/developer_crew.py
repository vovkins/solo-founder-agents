"""Developer crew for implementing features."""

from crewai import Crew, Process

from src.crews.types import CrewResult


def create_developer_crew(
    issue_number: int,
    verbose: bool = True,
) -> Crew:
    """Create a crew with only the Developer agent."""
    from src.agents import get_developer_agent
    developer_agent = get_developer_agent()
    from src.tasks import (
        create_analyze_task_task,
        create_implement_feature_task,
        create_write_tests_task,
    )

    analyze_task = create_analyze_task_task(issue_number)
    implement = create_implement_feature_task()
    write_tests = create_write_tests_task()

    return Crew(
        agents=[developer_agent],
        tasks=[analyze_task, implement, write_tests],
        process=Process.sequential,
        verbose=verbose,
    )


def run_developer_crew(issue_number: int) -> CrewResult:
    """Run the developer crew."""
    import logging
    from src.tools.file_permissions import set_current_role

    logger = logging.getLogger(__name__)
    set_current_role("developer")

    try:
        crew = create_developer_crew(issue_number)
        result = crew.kickoff()
        return {
            "status": "completed",
            "result": result.raw if hasattr(result, 'raw') else str(result),
            "issue_number": issue_number,
            "files_created": True,  # Developer saves files via save_artifact
        }
    except Exception as e:
        logger.error(f"Developer crew failed: {e}")
        return {"status": "error", "error": str(e), "issue_number": issue_number}
