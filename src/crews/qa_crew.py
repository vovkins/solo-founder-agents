"""QA crew for testing tasks."""

from typing import List, Optional

from crewai import Crew, Process


def create_qa_crew(
    pr_url: str = "",
    acceptance_criteria: Optional[List[str]] = None,
    verbose: bool = True,
) -> Crew:
    """Create a crew with only the QA agent."""
    from src.agents import qa_agent
    from src.tasks import (
        create_test_plan_task,
        create_e2e_tests_task,
        create_acceptance_verification_task,
        create_qa_signoff_task,
    )

    acceptance = acceptance_criteria or []
    test_plan = create_test_plan_task(pr_url, acceptance)
    e2e_tests = create_e2e_tests_task([], "Feature")
    verify = create_acceptance_verification_task(pr_url, acceptance, "{{test_results}}")
    signoff = create_qa_signoff_task(pr_url, "{{test_results}}", "{{acceptance_status}}")

    return Crew(
        agents=[qa_agent],
        tasks=[test_plan, e2e_tests, verify, signoff],
        process=Process.sequential,
        verbose=verbose,
    )


def run_qa_crew(pr_url: str = "", acceptance_criteria: Optional[List[str]] = None) -> dict:
    """Run the QA crew."""
    import logging
    from src.tools.file_permissions import set_current_role

    logger = logging.getLogger(__name__)
    set_current_role("qa")

    try:
        crew = create_qa_crew(pr_url, acceptance_criteria)
        result = crew.kickoff()
        return {"status": "completed", "result": str(result)}
    except Exception as e:
        logger.error(f"QA crew failed: {e}")
        return {"status": "error", "error": str(e)}
