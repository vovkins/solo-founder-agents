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
        """Get an issue by number."""
        return self.repo.get_issue(issue_number)

    def create_issue(
        self,
        title: str,
        body: str,
        labels: Optional[List[str]] = None,
        assignees: Optional[List[str]] = None,
    ) -> Issue.Issue:
        """Create a new issue."""
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

        Note: PyGithub's issue.edit() returns None, so we re-fetch the issue
        to return the updated object.
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
        issue.edit(**kwargs)
        # Re-fetch to get updated state
        return self.get_issue(issue_number)

    def add_label(self, issue_number: int, label: str) -> None:
        """Add a label to an issue."""
        issue = self.get_issue(issue_number)
        issue.add_to_labels(label)

    def remove_label(self, issue_number: int, label: str) -> None:
        """Remove a label from an issue."""
        issue = self.get_issue(issue_number)
        issue.remove_from_labels(label)

    def list_issues(
        self,
        state: str = "open",
        labels: Optional[List[str]] = None,
        limit: int = 100,
    ) -> List[Issue.Issue]:
        """List issues in the repository."""
        kwargs = {"state": state}
        if labels:
            kwargs["labels"] = ",".join(labels)
        
        # Get issues and limit manually
        issues = self.repo.get_issues(**kwargs)
        result = []
        for i, issue in enumerate(issues):
            if i >= limit:
                break
            result.append(issue)
        return result

    # ===========================================
    # File Operations
    # ===========================================

    def get_file(self, path: str, branch: str = "main") -> ContentFile:
        """Get file content from repository."""
        return self.repo.get_contents(path, ref=branch)

    def create_file(
        self,
        path: str,
        content: str,
        message: str,
        branch: str = "main",
    ) -> dict:
        """Create a new file in the repository."""
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
        """Update an existing file."""
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
        """Delete a file from the repository."""
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
        """Create a new branch."""
        ref = self.repo.get_git_ref(f"heads/{base_branch}")
        self.repo.create_git_ref(f"refs/heads/{branch_name}", sha=ref.object.sha)
        return branch_name

    def get_branch(self, branch_name: str):
        """Get a branch."""
        return self.repo.get_branch(branch_name)

    def delete_branch(self, branch_name: str) -> None:
        """Delete a branch."""
        ref = self.repo.get_git_ref(f"heads/{branch_name}")
        ref.delete()

    # ===========================================
    # Pull Request Operations
    # ===========================================

    def create_pull_request(
        self,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str = "main",
    ):
        """Create a pull request."""
        return self.repo.create_pull(
            title=title,
            body=body,
            head=head_branch,
            base=base_branch,
        )

    def get_pull_request(self, pr_number: int):
        """Get a pull request by number."""
        return self.repo.get_pull(pr_number)

    def list_pull_requests(self, state: str = "open", limit: int = 100):
        """List pull requests."""
        prs = self.repo.get_pulls(state=state)
        result = []
        for i, pr in enumerate(prs):
            if i >= limit:
                break
            result.append(pr)
        return result

    def merge_pull_request(self, pr_number: int) -> bool:
        """Merge a pull request."""
        pr = self.get_pull_request(pr_number)
        pr.merge()
        return True


# Global client instance
github_client = GitHubClient()
