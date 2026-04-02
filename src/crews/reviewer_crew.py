"""Reviewer crew for code review tasks."""

from crewai import Crew, Process


def create_reviewer_crew(
    pr_url: str = "",
    pr_description: str = "",
    verbose: bool = True,
) -> Crew:
    """Create a crew with only the Reviewer agent."""
    from src.agents import reviewer_agent
    from src.tasks import (
        create_review_pr_task,
        create_check_standards_task,
        create_security_check_task,
    )

    review_pr = create_review_pr_task(pr_url, pr_description)

    return Crew(
        agents=[reviewer_agent],
        tasks=[review_pr],
        process=Process.sequential,
        verbose=verbose,
    )


def run_reviewer_crew(pr_url: str, pr_description: str = "") -> dict:
    """Run the reviewer crew."""
    from src.tools.file_permissions import set_current_role
    set_current_role("reviewer")

    crew = create_reviewer_crew(pr_url, pr_description)
    result = crew.kickoff()

    return {
        "status": "completed",
        "result": str(result),
    }
