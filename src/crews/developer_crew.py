"""Developer crew for implementing features."""

from crewai import Crew, Process


def create_developer_crew(
    issue_number: int,
    verbose: bool = True,
) -> Crew:
    """Create a crew with only the Developer agent."""
    from src.agents import get_developer_agent
    developer_agent = get_developer_agent()
    from src.tasks import (
        create_analyze_task_task,
        create_feature_branch_task,
        create_implement_feature_task,
        create_write_tests_task,
        create_pull_request_task,
    )

    analyze_task = create_analyze_task_task(issue_number)
    create_branch = create_feature_branch_task(issue_number, "feature")
    implement = create_implement_feature_task("{{implementation_plan}}", "{{branch_name}}")
    write_tests = create_write_tests_task(["{{files_modified}}"], issue_number)
    create_pr = create_pull_request_task(issue_number, "{{branch_name}}", "{{changes_summary}}")

    return Crew(
        agents=[developer_agent],
        tasks=[analyze_task, create_branch, implement, write_tests, create_pr],
        process=Process.sequential,
        verbose=verbose,
    )


def run_developer_crew(issue_number: int) -> dict:
    """Run the developer crew."""
    import logging
    from src.tools.file_permissions import set_current_role

    logger = logging.getLogger(__name__)
    set_current_role("developer")

    try:
        crew = create_developer_crew(issue_number)
        result = crew.kickoff()
        return {"status": "completed", "result": str(result), "issue_number": issue_number}
    except Exception as e:
        logger.error(f"Developer crew failed: {e}")
        return {"status": "error", "error": str(e), "issue_number": issue_number}
