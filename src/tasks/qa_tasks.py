"""Tasks for QA Engineer agent."""

from crewai import Task

from src.agents import get_qa_agent


def create_test_plan_task(pr_url: str, acceptance_criteria: list) -> Task:
    """Create task for planning test cases.

    Args:
        pr_url: Pull Request URL
        acceptance_criteria: List of acceptance criteria

    Returns:
        Task for test planning
    """
    criteria_str = "\n".join(f"- {c}" for c in acceptance_criteria)

    return Task(
        description=f"""
        Create a test plan for the Pull Request.
        
        PR: {pr_url}
        
        Acceptance Criteria:
        {criteria_str}
        
        Your job is to:
        
        1. **Analyze Acceptance Criteria**
           - Understand each criterion
           - Identify test scenarios
           - Determine test types needed
        
        2. **Create Test Cases**
           - Happy path tests
           - Edge case tests
           - Error scenario tests
           - Integration tests
           - E2E tests
        
        3. **Prioritize Tests**
           - Critical: Must pass
           - High: Should pass
           - Medium: Nice to have
           - Low: Optional
        
        4. **Document Test Plan**
           - Test case descriptions
           - Expected results
           - Test data needed
        
        Output a structured test plan.
        """,
        expected_output="Test plan with test cases",
        agent=get_qa_agent(),
    )


def create_e2e_tests_task(test_cases: list, feature_name: str) -> Task:
    """Create task for running E2E tests.

    Args:
        test_cases: List of test cases to execute
        feature_name: Name of the feature being tested

    Returns:
        Task for E2E testing
    """
    cases_str = "\n".join(f"- {c}" for c in test_cases)

    return Task(
        description=f"""
        Execute E2E tests for {feature_name}.
        
        Test Cases:
        {cases_str}
        
        Your job is to:
        
        1. **Setup Environment**
           - Ensure test environment ready
           - Setup test data
           - Configure test settings
        
        2. **Execute Tests**
           - Run each test case
           - Record results
           - Capture screenshots for failures
           - Note any anomalies
        
        3. **Document Results**
           - Pass/Fail for each test
           - Steps to reproduce failures
           - Screenshots/evidence
           - Environment details
        
        Use Playwright or Detox for E2E testing.
        Document all results.
        """,
        expected_output="E2E test results with pass/fail status",
        agent=get_qa_agent(),
    )


def create_integration_tests_task(
    test_scenarios: list,
    api_endpoints: list,
) -> Task:
    """Create task for integration testing.

    Args:
        test_scenarios: Integration test scenarios
        api_endpoints: API endpoints to test

    Returns:
        Task for integration testing
    """
    scenarios_str = "\n".join(f"- {s}" for s in test_scenarios)
    endpoints_str = "\n".join(f"- {e}" for e in api_endpoints)

    return Task(
        description=f"""
        Execute integration tests.
        
        Test Scenarios:
        {scenarios_str}
        
        API Endpoints:
        {endpoints_str}
        
        Your job is to:
        
        1. **API Testing**
           - Test each endpoint
           - Verify request/response
           - Test error handling
           - Check authentication
        
        2. **Database Testing**
           - Verify data persistence
           - Test transactions
           - Check constraints
        
        3. **Integration Points**
           - External services
           - State management
           - Event handling
        
        4. **Document Results**
           - Test results
           - Response times
           - Error details
        
        Use Jest + Supertest for API testing.
        """,
        expected_output="Integration test results",
        agent=get_qa_agent(),
    )


def create_acceptance_verification_task(
    pr_url: str,
    acceptance_criteria: list,
    test_results: dict,
) -> Task:
    """Create task for verifying acceptance criteria.

    Args:
        pr_url: Pull Request URL
        acceptance_criteria: Acceptance criteria list
        test_results: Results from testing

    Returns:
        Task for acceptance verification
    """
    criteria_str = "\n".join(f"- {c}" for c in acceptance_criteria)

    return Task(
        description=f"""
        Verify all acceptance criteria are met.
        
        PR: {pr_url}
        
        Acceptance Criteria:
        {criteria_str}
        
        Test Results:
        {test_results}
        
        Your job is to:
        
        1. **Review Each Criterion**
           - Check if tests cover it
           - Verify test passed
           - Document evidence
        
        2. **Identify Gaps**
           - Missing test coverage
           - Incomplete criteria
           - Edge cases not covered
        
        3. **Make Assessment**
           - All criteria met → Approve
           - Some criteria not met → List issues
           - Critical issues → Block
        
        Output acceptance verification report.
        """,
        expected_output="Acceptance criteria verification report",
        agent=get_qa_agent(),
    )


def create_bug_report_task(
    issue_description: str,
    steps_to_reproduce: list,
    severity: str,
) -> Task:
    """Create task for reporting a bug.

    Args:
        issue_description: Description of the bug
        steps_to_reproduce: Steps to reproduce
        severity: Bug severity (Critical/High/Medium/Low)

    Returns:
        Task for bug reporting
    """
    steps_str = "\n".join(f"{i+1}. {s}" for i, s in enumerate(steps_to_reproduce))

    return Task(
        description=f"""
        Create a bug report for the issue found.
        
        Issue: {issue_description}
        Severity: {severity}
        
        Steps to Reproduce:
        {steps_str}
        
        Your job is to:
        
        1. **Create GitHub Issue**
           - Use bug template
           - Include all details
           - Add severity label
           - Link to PR/feature
        
        2. **Document Evidence**
           - Screenshots
           - Logs
           - Environment details
        
        3. **Categorize**
           - Severity level
           - Component affected
           - Type of issue
        
        Use templates/github-issue-bug.md template.
        Create issue in GitHub.
        """,
        expected_output="URL of created bug report issue",
        agent=get_qa_agent(),
    )


def create_qa_signoff_task(
    pr_url: str,
    test_results: dict,
    acceptance_status: str,
) -> Task:
    """Create task for QA sign-off.

    Args:
        pr_url: Pull Request URL
        test_results: All test results
        acceptance_status: Acceptance criteria status

    Returns:
        Task for sign-off
    """
    return Task(
        description=f"""
        Provide QA sign-off for the Pull Request.
        
        PR: {pr_url}
        
        Test Results:
        {test_results}
        
        Acceptance Status: {acceptance_status}
        
        Your job is to:
        
        1. **Final Review**
           - All tests passed
           - All acceptance criteria met
           - No blocking issues
           - Ready for production
        
        2. **Sign Off Decision**
           - APPROVE: Ready to merge
           - BLOCK: Issues must be fixed
           - CONDITIONAL: Minor issues, can merge
        
        3. **Document Sign-Off**
           - Sign-off status
           - Test summary
           - Any notes
        
        Add QA sign-off comment to PR.
        Update task status based on sign-off.
        
        IMPORTANT: Only sign off if ALL acceptance criteria are met.
        """,
        expected_output="QA sign-off status (Approved/Blocked/Conditional)",
        agent=get_qa_agent(),
    )


def create_regression_test_task(
    pr_url: str,
    fixed_issues: list,
) -> Task:
    """Create task for regression testing after fixes.

    Args:
        pr_url: Pull Request URL
        fixed_issues: List of issues that were fixed

    Returns:
        Task for regression testing
    """
    issues_str = "\n".join(f"- {i}" for i in fixed_issues)

    return Task(
        description=f"""
        Perform regression testing after bug fixes.
        
        PR: {pr_url}
        
        Fixed Issues:
        {issues_str}
        
        Your job is to:
        
        1. **Verify Fixes**
           - Test each fixed issue
           - Confirm fix works
           - Check original test case
        
        2. **Regression Check**
           - Test related functionality
           - Check for new issues
           - Verify existing tests still pass
        
        3. **Update Tests**
           - Add tests for fixed issues
           - Prevent future regressions
        
        4. **Document Results**
           - Fix verification
           - Regression status
           - Any new issues
        
        Output regression test report.
        """,
        expected_output="Regression test results",
        agent=get_qa_agent(),
    )
