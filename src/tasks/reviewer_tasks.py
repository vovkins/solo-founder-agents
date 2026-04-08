"""Tasks for Developer (Reviewer) agent."""

from crewai import Task

from src.agents import get_reviewer_agent


def create_review_pr_task(pr_url: str, pr_description: str) -> Task:
    """Create task for reviewing a Pull Request.

    Args:
        pr_url: URL of the Pull Request
        pr_description: Description from the PR

    Returns:
        Task for PR review
    """
    return Task(
        description=f"""
        Review the Pull Request.
        
        PR URL: {pr_url}
        
        PR Description:
        {pr_description}
        
        Your job is to:
        1. Fetch PR files changed from GitHub
        2. Review each file for:
           - Code quality and readability
           - Correctness and edge cases
           - Security vulnerabilities
           - Performance issues
           - Test coverage
           - Coding standards compliance
        
        3. Leave comments on specific lines if needed
        4. Provide overall assessment
        
        Review Criteria:
        - PR should be under 1000 lines
        - Tests should cover new code
        - No security vulnerabilities
        - Follows coding standards
        - Handles errors properly
        
        Be constructive and specific in feedback.
        """,
        expected_output="Review summary with comments and approval status",
        agent=get_reviewer_agent(),
    )


def create_check_standards_task(pr_files: list) -> Task:
    """Create task for checking coding standards.

    Args:
        pr_files: List of files in the PR

    Returns:
        Task for standards check
    """
    files_str = "\n".join(f"- {f}" for f in pr_files)

    return Task(
        description=f"""
        Check coding standards compliance.
        
        Files to check:
        {files_str}
        
        Check for:
        
        1. **TypeScript Standards**
           - Strict mode enabled
           - No `any` types
           - Proper interfaces
           - Type safety
        
        2. **React Standards**
           - Functional components
           - Hooks used correctly
           - Props interfaces defined
           - No prop drilling issues
        
        3. **Node.js Standards**
           - async/await used
           - Proper error handling
           - Input validation
           - Clean separation
        
        4. **Naming Conventions**
           - Files: camelCase or PascalCase
           - Variables: camelCase
           - Components: PascalCase
           - Constants: UPPER_SNAKE_CASE
        
        5. **Code Organization**
           - Logical file structure
           - Proper imports
           - No circular dependencies
        
        Report any violations with file and line numbers.
        """,
        expected_output="Standards compliance report",
        agent=get_reviewer_agent(),
    )


def create_security_check_task(pr_files: list) -> Task:
    """Create task for security review.

    Args:
        pr_files: List of files in the PR

    Returns:
        Task for security check
    """
    files_str = "\n".join(f"- {f}" for f in pr_files)

    return Task(
        description=f"""
        Perform security review of the code.
        
        Files to review:
        {files_str}
        
        Check for:
        
        1. **Injection Vulnerabilities**
           - SQL injection
           - XSS (Cross-site scripting)
           - Command injection
           - NoSQL injection
        
        2. **Authentication/Authorization**
           - Proper session handling
           - Token validation
           - Password handling
           - Permission checks
        
        3. **Data Protection**
           - Sensitive data in logs
           - Proper encryption
           - Secure API keys storage
           - Input sanitization
        
        4. **Dependencies**
           - Known vulnerabilities
           - Outdated packages
           - Unnecessary dependencies
        
        5. **Other Issues**
           - Insecure defaults
           - Missing rate limiting
           - CORS misconfiguration
        
        Report any security issues found with severity (Critical/High/Medium/Low).
        """,
        expected_output="Security review report",
        agent=get_reviewer_agent(),
    )


def create_review_tests_task(test_files: list) -> Task:
    """Create task for reviewing test coverage.

    Args:
        test_files: List of test files in the PR

    Returns:
        Task for test review
    """
    files_str = "\n".join(f"- {f}" for f in test_files)

    return Task(
        description=f"""
        Review test coverage and quality.
        
        Test files:
        {files_str}
        
        Your job is to:
        
        1. **Coverage Check**
           - All new functions tested?
           - Edge cases covered?
           - Error paths tested?
        
        2. **Test Quality**
           - Tests are meaningful?
           - Testing behavior not implementation?
           - Proper assertions?
           - Good test names?
        
        3. **Test Patterns**
           - Arrange-Act-Assert pattern
           - Proper mocking
           - No flaky tests
           - Independent tests
        
        4. **Missing Tests**
           - Identify untested code
           - Suggest additional tests
           - Note edge cases to cover
        
        Provide a test coverage assessment.
        """,
        expected_output="Test coverage review report",
        agent=get_reviewer_agent(),
    )


def create_approval_task(
    pr_url: str,
    review_summary: str,
    issues_found: list,
) -> Task:
    """Create task for final approval decision.

    Args:
        pr_url: Pull Request URL
        review_summary: Summary of the review
        issues_found: List of issues found during review

    Returns:
        Task for approval decision
    """
    issues_str = "\n".join(f"- {issue}" for issue in issues_found) if issues_found else "No issues found"

    return Task(
        description=f"""
        Make final approval decision for PR.
        
        PR: {pr_url}
        
        Review Summary:
        {review_summary}
        
        Issues Found:
        {issues_str}
        
        Your job is to:
        
        1. **Assess Severity**
           - Critical: Must fix before merge
           - High: Should fix
           - Medium: Nice to fix
           - Low: Can be addressed later
        
        2. **Make Decision**
           - APPROVE if no critical/high issues
           - REQUEST CHANGES if blocking issues
           - COMMENT for non-blocking feedback
        
        3. **Submit Review**
           - Add review summary
           - Submit with appropriate status
        
        Guidelines:
        - Be fair and constructive
        - Don't block on style preferences
        - Focus on correctness and security
        - Consider PR scope
        
        Submit the review via GitHub API.
        """,
        expected_output="Review submitted (Approved/Changes Requested/Commented)",
        agent=get_reviewer_agent(),
    )
