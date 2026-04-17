"""Tasks for QA Engineer agent."""

from crewai import Task

from src.agents import get_qa_agent


def create_test_plan_task() -> Task:
    """Create task for planning test cases based on artifacts in GitHub.

    Returns:
        Task for test planning
    """
    return Task(
        description="""
        Create a test plan by analyzing project artifacts in GitHub.

        Your job is to:
        1. Read task specifications from docs/requirements/task-specs.md using read_artifact tool
        2. Read the PRD from docs/requirements/prd.md for acceptance criteria
        3. Review the design system from docs/design/design-system.md
        4. Read the implemented source code files in src/ using read_artifact tool

        Based on what you find, create a structured test plan covering:
        - Test cases derived from acceptance criteria in PRD and task-specs
        - Test cases for each implemented component/file in src/
        - Happy path, edge case, and error scenario tests
        - Priority: Critical / High / Medium / Low

        Save the test plan using save_artifact with type="test-case".

        Output a summary of the test plan.
        """,
        expected_output="Structured test plan with test cases derived from PRD, task-specs, and implemented code",
        output_key="test_plan",
        agent=get_qa_agent(),
    )


def create_code_verification_task() -> Task:
    """Create task for verifying code against requirements.

    Returns:
        Task for code verification
    """
    return Task(
        description="""
        Verify that the implemented code meets the requirements.

        Based on the test plan from the previous step, verify the implementation:

        Your job is to:
        1. Read each source file in src/ using read_artifact tool
        2. For each file, check:
           - Does it implement the requirements from task-specs?
           - Does it follow the design system guidelines?
           - Are there TypeScript errors or obvious bugs?
           - Is error handling present?
           - Are there security concerns (hardcoded secrets, injection risks)?
        3. Check that unit tests exist and cover the implemented functionality
        4. Document findings: pass / warning / fail for each check

        You are doing STATIC CODE REVIEW and REQUIREMENTS VERIFICATION.
        You do NOT need to run the code — analyze it by reading the files.

        Save the verification report using save_artifact with type="test-run-log".

        Output a summary: list of passed checks and list of issues found.
        """,
        expected_output="Verification report: which checks passed, which issues found",
        output_key="verification_results",
        agent=get_qa_agent(),
    )


def create_qa_signoff_task() -> Task:
    """Create task for QA sign-off.

    Returns:
        Task for sign-off
    """
    return Task(
        description="""
        Provide QA sign-off based on test plan and verification results.

        Review the test plan and verification results from previous steps.

        Your job is to:
        1. Review all findings from the verification step
        2. Make a sign-off decision:
           - APPROVE: All critical checks pass, no blocking issues
           - BLOCK: Critical issues found that must be fixed
           - CONDITIONAL: Minor issues, acceptable with notes
        3. Document the sign-off with:
           - Overall status (Approved/Blocked/Conditional)
           - Summary of checks performed
           - List of issues (if any) with severity
           - Recommendations

        Save the sign-off document using save_artifact with type="qa-signoff".

        IMPORTANT: Only APPROVE if there are no Critical or High severity issues.
        """,
        expected_output="QA sign-off status: Approved, Blocked, or Conditional with details",
        agent=get_qa_agent(),
    )
