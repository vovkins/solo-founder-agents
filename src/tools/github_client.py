"""GitHub API client for repository operations."""

from typing import List, Optional

from github import Github, Issue, Repository
from github.ContentFile import ContentFile

from config.settings import settings


class GitHubClient:
    """Client for GitHub API operations."""

    def __init__(self):
        """Initialize GitHub client with token from settings."""
        self.client = Github(settings.github_token)
        self._repo: Optional[Repository.Repository] = None

    @property
    def repo(self) -> Repository.Repository:
        """Get the repository instance."""
        if self._repo is None:
            self._repo = self.client.get_repo(settings.github_repo)
        return self._repo

    # ===========================================
    # Issue Operations
    # ===========================================

    def get_issue(self, issue_number: int) -> Issue.Issue:
        """Get an issue by number.

        Args:
            issue_number: Issue number

        Returns:
            Issue instance
        """
        return self.repo.get_issue(issue_number)

    def create_issue(
        self,
        title: str,
        body: str,
        labels: Optional[List[str]] = None,
        assignees: Optional[List[str]] = None,
    ) -> Issue.Issue:
        """Create a new issue.

        Args:
            title: Issue title
            body: Issue body/description
            labels: List of label names
            assignees: List of assignee usernames

        Returns:
            Created Issue instance
        """
        return self.repo.create_issue(
            title=title,
            body=body,
            labels=labels or [],
            assignees=assignees or [],
        )

    def update_issue(
        self,
        issue_number: int,
        title: Optional[str] = None,
        body: Optional[str] = None,
        labels: Optional[List[str]] = None,
        state: Optional[str] = None,
    ) -> Issue.Issue:
        """Update an existing issue.

        Args:
            issue_number: Issue number
            title: New title (optional)
            body: New body (optional)
            labels: New labels (optional)
            state: New state ('open' or 'closed')

        Returns:
            Updated Issue instance
        """
        issue = self.get_issue(issue_number)
        kwargs = {}
        if title:
            kwargs["title"] = title
        if body:
            kwargs["body"] = body
        if labels:
            kwargs["labels"] = labels
        if state:
            kwargs["state"] = state
        return issue.edit(**kwargs)

    def add_label(self, issue_number: int, label: str) -> None:
        """Add a label to an issue.

        Args:
            issue_number: Issue number
            label: Label name to add
        """
        issue = self.get_issue(issue_number)
        issue.add_to_labels(label)

    def remove_label(self, issue_number: int, label: str) -> None:
        """Remove a label from an issue.

        Args:
            issue_number: Issue number
            label: Label name to remove
        """
        issue = self.get_issue(issue_number)
        issue.remove_from_labels(label)

    def list_issues(
        self,
        state: str = "open",
        labels: Optional[List[str]] = None,
        limit: int = 100,
    ) -> List[Issue.Issue]:
        """List issues in the repository.

        Args:
            state: Issue state ('open', 'closed', 'all')
            labels: Filter by labels
            limit: Maximum number of issues to return

        Returns:
            List of Issue instances
        """
        kwargs = {"state": state}
        if labels:
            kwargs["labels"] = ",".join(labels)
        return list(self.repo.get_issues(**kwargs)[:limit])

    # ===========================================
    # File Operations
    # ===========================================

    def get_file(self, path: str, branch: str = "main") -> ContentFile:
        """Get file content from repository.

        Args:
            path: File path in repository
            branch: Branch name

        Returns:
            ContentFile instance
        """
        return self.repo.get_contents(path, ref=branch)

    def read_file(self, path: str, branch: str = "main") -> str:
        """Read file content as string.

        Args:
            path: File path in repository
            branch: Branch name

        Returns:
            File content as string
        """
        content = self.get_file(path, branch)
        return content.decoded_content.decode("utf-8")

    def create_file(
        self,
        path: str,
        content: str,
        message: str,
        branch: str = "main",
    ) -> dict:
        """Create a new file in repository.

        Args:
            path: File path in repository
            content: File content
            message: Commit message
            branch: Branch name

        Returns:
            GitHub API response
        """
        return self.repo.create_file(
            path=path,
            message=message,
            content=content,
            branch=branch,
        )

    def update_file(
        self,
        path: str,
        content: str,
        message: str,
        branch: str = "main",
    ) -> dict:
        """Update an existing file in repository.

        Args:
            path: File path in repository
            content: New file content
            message: Commit message
            branch: Branch name

        Returns:
            GitHub API response
        """
        file = self.get_file(path, branch)
        return self.repo.update_file(
            path=path,
            message=message,
            content=content,
            sha=file.sha,
            branch=branch,
        )

    def delete_file(
        self,
        path: str,
        message: str,
        branch: str = "main",
    ) -> dict:
        """Delete a file from repository.

        Args:
            path: File path in repository
            message: Commit message
            branch: Branch name

        Returns:
            GitHub API response
        """
        file = self.get_file(path, branch)
        return self.repo.delete_file(
            path=path,
            message=message,
            sha=file.sha,
            branch=branch,
        )

    # ===========================================
    # Branch Operations
    # ===========================================

    def create_branch(self, branch_name: str, base_branch: str = "main") -> str:
        """Create a new branch.

        Args:
            branch_name: New branch name
            base_branch: Base branch to create from

        Returns:
            New branch name
        """
        ref = self.repo.get_git_ref(f"heads/{base_branch}")
        self.repo.create_git_ref(f"refs/heads/{branch_name}", ref.object.sha)
        return branch_name

    def create_pull_request(
        self,
        title: str,
        body: str,
        head: str,
        base: str = "main",
        draft: bool = False,
    ) -> dict:
        """Create a pull request.

        Args:
            title: PR title
            body: PR body/description
            head: Head branch name
            base: Base branch name
            draft: Whether to create as draft

        Returns:
            PullRequest instance
        """
        return self.repo.create_pull(
            title=title,
            body=body,
            head=head,
            base=base,
            draft=draft,
        )


# Global client instance
github_client = GitHubClient()
