"""GitHub tools for CrewAI agents."""

from typing import List, Optional

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from config.settings import settings
from .github_client import github_client


# ===========================================
# Issue Tools
# ===========================================


def create_github_issue(
    title: str,
    body: str,
    labels: Optional[List[str]] = None,
) -> dict:
    """Create a GitHub issue and return its info.

    Args:
        title: Issue title
        body: Issue description
        labels: List of label names to apply

    Returns:
        Dict with 'number', 'url', 'title' of the created issue
    """
    issue = github_client.create_issue(title, body, labels or [])
    return {
        "number": issue.number,
        "url": issue.html_url,
        "title": issue.title
    }


def update_github_issue(
    issue_number: int,
    title: Optional[str] = None,
    body: Optional[str] = None,
    labels: Optional[List[str]] = None,
    state: Optional[str] = None,
) -> str:
    """Update a GitHub issue and return its URL.

    Args:
        issue_number: Issue number
        title: New title (optional)
        body: New body (optional)
        labels: New labels (optional)
        state: New state ('open' or 'closed')

    Returns:
        URL of the updated issue
    """
    issue = github_client.update_issue(issue_number, title, body, labels, state)
    return issue.html_url


def add_label_to_issue(issue_number: int, label: str) -> str:
    """Add a label to an existing issue.

    Args:
        issue_number: Issue number
        label: Label name to add

    Returns:
        URL of the updated issue
    """
    github_client.add_label(issue_number, label)
    issue = github_client.get_issue(issue_number)
    return issue.html_url


def close_issue(issue_number: int) -> str:
    """Close a GitHub issue.

    Args:
        issue_number: Issue number to close

    Returns:
        URL of the closed issue
    """
    issue = github_client.update_issue(issue_number, state="closed")
    return issue.html_url


def get_issue_details(issue_number: int) -> dict:
    """Get details of a GitHub issue.

    Args:
        issue_number: Issue number

    Returns:
        Dictionary with issue details
    """
    issue = github_client.get_issue(issue_number)
    return {
        "number": issue.number,
        "title": issue.title,
        "body": issue.body,
        "state": issue.state,
        "labels": [label.name for label in issue.labels],
        "url": issue.html_url,
        "created_at": issue.created_at.isoformat(),
        "updated_at": issue.updated_at.isoformat(),
    }


def list_open_issues(labels: Optional[List[str]] = None) -> List[dict]:
    """List open issues in the repository.

    Args:
        labels: Filter by labels (optional)

    Returns:
        List of issue dictionaries
    """
    issues = github_client.list_issues(state="open", labels=labels)
    return [
        {
            "number": issue.number,
            "title": issue.title,
            "labels": [label.name for label in issue.labels],
            "url": issue.html_url,
        }
        for issue in issues
    ]


# ===========================================
# File Tools
# ===========================================


def read_file_from_repo(path: str, branch: str = settings.github_default_branch) -> str:
    """Read a file from the repository.

    Args:
        path: File path in repository
        branch: Branch name (default: main)

    Returns:
        File content as string
    """
    file = github_client.get_file(path, branch)
    return file.decoded_content.decode("utf-8")


def create_file_in_repo(
    path: str,
    content: str,
    message: str,
    branch: str = settings.github_default_branch,
) -> str:
    """Create a new file in the repository.

    Args:
        path: File path in repository
        content: File content
        message: Commit message
        branch: Branch name (default: main)

    Returns:
        URL to the created file
    """
    github_client.create_file(path, content, message, branch)
    return f"https://github.com/{github_client.repo.full_name}/blob/{branch}/{path}"


def update_file_in_repo(
    path: str,
    content: str,
    message: str,
    branch: str = settings.github_default_branch,
) -> str:
    """Update an existing file in the repository.

    Args:
        path: File path in repository
        content: New file content
        message: Commit message
        branch: Branch name (default: main)

    Returns:
        URL to the updated file
    """
    github_client.update_file(path, content, message, branch)
    return f"https://github.com/{github_client.repo.full_name}/blob/{branch}/{path}"


# ===========================================
# Pull Request Tools
# ===========================================


def create_pull_request(
    title: str,
    body: str,
    head_branch: str,
    base_branch: str = settings.github_default_branch,
) -> str:
    """Create a pull request.

    Args:
        title: PR title
        body: PR description
        head_branch: Head branch name
        base_branch: Base branch name (default: main)

    Returns:
        URL of the created PR
    """
    pr = github_client.create_pull_request(title, body, head_branch, base_branch)
    return pr.html_url


# ===========================================
# Pydantic Models for Tool Arguments
# ===========================================


class CreateGitHubIssueToolInput(BaseModel):
    """Input schema for GitHub issue creation."""
    title: str = Field(description="Issue title")
    body: str = Field(description="Issue description")
    labels: Optional[List[str]] = Field(default=None, description="Optional labels")


class ListOpenIssuesToolInput(BaseModel):
    """Input schema for listing open issues."""
    labels: Optional[List[str]] = Field(default=None, description="Filter by labels")


class CreatePullRequestToolInput(BaseModel):
    """Input schema for PR creation."""
    title: str = Field(description="PR title")
    body: str = Field(description="PR description")
    head_branch: str = Field(description="Head branch name")
    base_branch: str = Field(default=settings.github_default_branch, description="Base branch name")


# ===========================================
# CrewAI Tools
# ===========================================


class CreateGitHubIssueTool(BaseTool):
    """Tool for creating GitHub issues."""

    name: str = "create_github_issue"
    description: str = "Create a GitHub issue with title, body, and optional labels"
    args_schema: type[BaseModel] = CreateGitHubIssueToolInput

    def _run(self, title: str, body: str, labels: Optional[List[str]] = None) -> str:
        result = create_github_issue(title, body, labels)
        return f"✅ Created issue #{result['number']}: {result['url']}"


class ListOpenIssuesTool(BaseTool):
    """Tool for listing open GitHub issues."""

    name: str = "list_open_issues"
    description: str = "List all open GitHub issues in the repository"
    args_schema: type[BaseModel] = ListOpenIssuesToolInput

    def _run(self, labels: Optional[List[str]] = None) -> str:
        issues = list_open_issues(labels)
        if not issues:
            return "No open issues found."
        return "\n".join([f"#{issue['number']} — {issue['title']}" for issue in issues])


class CreatePullRequestTool(BaseTool):
    """Tool for creating Pull Requests."""

    name: str = "create_pull_request"
    description: str = "Create a Pull Request with title, body, and branch names"
    args_schema: type[BaseModel] = CreatePullRequestToolInput

    def _run(
        self,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str = settings.github_default_branch,
    ) -> str:
        """Create a Pull Request.

        Args:
            title: PR title
            body: PR description
            head_branch: Head branch name
            base_branch: Base branch name (default: main)

        Returns:
            URL of created PR or error message
        """
        try:
            pr_url = create_pull_request(title, body, head_branch, base_branch)
            return f"✅ Pull Request created: {pr_url}"
        except Exception as e:
            return f"❌ Failed to create PR: {str(e)}\n\nMake sure the branch exists and has been pushed to GitHub."


# Export tools
create_github_issue_tool = CreateGitHubIssueTool()
list_open_issues_tool = ListOpenIssuesTool()
create_pull_request_tool = CreatePullRequestTool()
