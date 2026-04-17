"""QA crew for testing tasks."""

from typing import List, Optional

from crewai import Crew, Process

from src.crews.types import CrewResult


def create_qa_crew(verbose: bool = True) -> Crew:
    """Create a crew with only the QA agent."""
    from src.agents import get_qa_agent
    qa_agent = get_qa_agent()
    from src.tasks import (
        create_test_plan_task,
        create_code_verification_task,
        create_qa_signoff_task,
    )

    test_plan = create_test_plan_task()
    verify = create_code_verification_task()
    signoff = create_qa_signoff_task()

    return Crew(
        agents=[qa_agent],
        tasks=[test_plan, verify, signoff],
        process=Process.sequential,
        verbose=verbose,
    )


def run_qa_crew() -> CrewResult:
    """Run the QA crew."""
    import logging
    from src.tools.file_permissions import set_current_role

    logger = logging.getLogger(__name__)
    set_current_role("qa")

    try:
        crew = create_qa_crew()
        result = crew.kickoff()
        return {"status": "completed", "result": str(result)}
    except Exception as e:
        logger.error(f"QA crew failed: {e}")
        return {"status": "error", "error": str(e)}
