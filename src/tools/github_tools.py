"""GitHub tools for CrewAI agents."""

from typing import List, Optional

from .github_client import github_client


# ===========================================
# Issue Tools
# ===========================================


def create_github_issue(
    title: str,
    body: str,
    labels: Optional[List[str]] = None,
) -> str:
    """Create a GitHub issue and return its URL.

    Args:
        title: Issue title
        body: Issue description
        labels: List of label names to apply

    Returns:
        URL of the created issue
    """
    issue = github_client.create_issue(title, body, labels or [])
    return issue.html_url


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


def read_file_from_repo(path: str, branch: str = "main") -> str:
    """Read a file from the repository.

    Args:
        path: File path in repository
        branch: Branch name (default: main)

    Returns:
        File content as string
    """
    return github_client.read_file(path, branch)


def create_file_in_repo(
    path: str,
    content: str,
    message: str,
    branch: str = "main",
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
    branch: str = "main",
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
    base_branch: str = "main",
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
