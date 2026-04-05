"""Reviewer crew for code review tasks."""

from crewai import Crew, Process


def create_reviewer_crew(
    pr_url: str = "",
    pr_description: str = "",
    verbose: bool = True,
) -> Crew:
    """Create a crew with only the Reviewer agent."""
    from src.agents import get_reviewer_agent
    reviewer_agent = get_reviewer_agent()
    from src.tasks import create_review_pr_task

    review_pr = create_review_pr_task(pr_url, pr_description)

    return Crew(
        agents=[reviewer_agent],
        tasks=[review_pr],
        process=Process.sequential,
        verbose=verbose,
    )


def run_reviewer_crew(pr_url: str, pr_description: str = "") -> dict:
    """Run the reviewer crew."""
    import logging
    from src.tools.file_permissions import set_current_role

    logger = logging.getLogger(__name__)
    set_current_role("reviewer")

    try:
        crew = create_reviewer_crew(pr_url, pr_description)
        result = crew.kickoff()
        return {"status": "completed", "result": str(result)}
    except Exception as e:
        logger.error(f"Reviewer crew failed: {e}")
        return {"status": "error", "error": str(e)}
