"""Tasks for Developer (Coder) agent."""

from crewai import Task

from src.agents import get_developer_agent


def create_analyze_task_task(issue_number: int) -> Task:
    """Create task for analyzing a GitHub Issue.

    Args:
        issue_number: GitHub Issue number

    Returns:
        Task for issue analysis
    """
    return Task(
        description=f"""
        Analyze GitHub Issue #{issue_number} for implementation.
        
        Your job is to:
        1. Read the issue details from GitHub
        2. Understand acceptance criteria
        3. Review related System Design documents
        4. Check for ADRs related to this task
        5. Identify dependencies
        6. Plan implementation approach
        
        Output:
        - Task summary
        - Acceptance criteria list
        - Implementation plan
        - Files to create/modify
        - Dependencies
        """,
        expected_output="Implementation plan for the task",
        agent=get_developer_agent(),
    )


def create_feature_branch_task(
    issue_number: int,
    feature_name: str,
) -> Task:
    """Create task for creating a feature branch.

    Args:
        issue_number: GitHub Issue number
        feature_name: Name for the branch

    Returns:
        Task for branch creation
    """
    branch_name = f"feature/{issue_number}-{feature_name}"

    return Task(
        description=f"""
        Create feature branch for implementation.
        
        Branch name: {branch_name}
        
        Your job is to:
        1. Ensure you're on main branch
        2. Pull latest changes
        3. Create new branch: {branch_name}
        
        Use git commands to create the branch.
        """,
        expected_output=f"Branch {branch_name} created and checked out",
        agent=get_developer_agent(),
    )


def create_implement_feature_task(
    implementation_plan: str,
    branch_name: str,
) -> Task:
    """Create task for implementing a feature.

    Args:
        implementation_plan: Plan from analysis
        branch_name: Feature branch name

    Returns:
        Task for implementation
    """
    return Task(
        description=f"""
        Implement the feature according to plan.
        
        Branch: {branch_name}
        
        Implementation Plan:
        {implementation_plan}
        
        Your job is to:
        1. Create necessary files
        2. Implement functionality
        3. Follow coding standards
        4. Handle errors appropriately
        5. Add necessary logging
        
        Code Guidelines:
        - Use TypeScript strict mode
        - Functional React components
        - Proper error handling
        - JSDoc comments for functions
        
        Ensure code is clean, readable, and maintainable.
        """,
        expected_output="Implementation complete with list of created/modified files",
        agent=get_developer_agent(),
    )


def create_write_tests_task(
    files_modified: list,
    issue_number: int,
) -> Task:
    """Create task for writing unit tests.

    Args:
        files_modified: List of files that were modified
        issue_number: GitHub Issue number

    Returns:
        Task for test writing
    """
    files_str = "\n".join(f"- {f}" for f in files_modified)

    return Task(
        description=f"""
        Write unit tests for the implemented feature.
        
        Files to test:
        {files_str}
        
        Your job is to:
        1. Create test files (filename.test.ts)
        2. Test all functions and components
        3. Cover edge cases
        4. Test error handling
        5. Ensure tests are meaningful
        
        Testing Guidelines:
        - Use Jest and React Testing Library
        - Test behavior, not implementation
        - Use descriptive test names
        - Arrange-Act-Assert pattern
        - Mock external dependencies
        
        Run tests to ensure they pass.
        """,
        expected_output="Unit tests written and passing",
        agent=get_developer_agent(),
    )


def create_pull_request_task(
    issue_number: int,
    branch_name: str,
    changes_summary: str,
) -> Task:
    """Create task for creating a Pull Request.

    Args:
        issue_number: GitHub Issue number
        branch_name: Feature branch name
        changes_summary: Summary of changes

    Returns:
        Task for PR creation
    """
    return Task(
        description=f"""
        Create Pull Request for the implemented feature.
        
        Branch: {branch_name}
        Issue: #{issue_number}
        
        Changes:
        {changes_summary}
        
        Your job is to:
        1. Push branch to remote
        2. Create PR with title: `feat: [feature description]`
        3. Add description with:
           - Summary of changes
           - Link to Issue #{issue_number}
           - Testing instructions
           - Screenshots (if UI changes)
        4. Request review from Developer (Reviewer)
        
        PR Guidelines:
        - Keep under 1000 lines
        - Clear description
        - All tests passing
        - No lint errors
        
        Create the PR using GitHub API.
        """,
        expected_output="URL of created Pull Request",
        agent=get_developer_agent(),
    )


def create_fix_review_comments_task(
    pr_url: str,
    review_comments: str,
) -> Task:
    """Create task for addressing review comments.

    Args:
        pr_url: Pull Request URL
        review_comments: Comments from reviewer

    Returns:
        Task for fixing comments
    """
    return Task(
        description=f"""
        Address review comments on Pull Request.
        
        PR: {pr_url}
        
        Review Comments:
        {review_comments}
        
        Your job is to:
        1. Read each comment
        2. Make necessary changes
        3. Respond to comments
        4. Push fixes
        5. Re-request review
        
        Guidelines:
        - Accept valid suggestions
        - Explain reasoning if you disagree
        - Keep changes minimal
        - Update tests if needed
        """,
        expected_output="Review comments addressed and fixes pushed",
        agent=get_developer_agent(),
    )
