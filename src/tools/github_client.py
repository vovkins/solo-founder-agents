"""GitHub API client for repository operations.

FIX: Added factory function for dependency injection.
"""

import logging
import re
import time
from typing import List, Optional
from functools import wraps

from github import Github, Issue, Repository, GithubException
from github.ContentFile import ContentFile

from config.settings import settings

logger = logging.getLogger(__name__)


def retry_on_rate_limit(max_retries: int = 3, delay: int = 60):
    """Decorator to retry on rate limit errors.
    
    Args:
        max_retries: Maximum number of retries
        delay: Delay in seconds between retries (default: 60s for rate limit)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except GithubException as e:
                    last_exception = e
                    if e.status == 403 and 'rate limit' in str(e).lower():
                        if attempt < max_retries - 1:
                            logger.warning(
                                f"Rate limit hit, waiting {delay}s before retry (attempt {attempt + 1}/{max_retries})"""
                                f"(attempt {attempt + 1}/{max_retries})"
                            )
                            time.sleep(delay)
                        else:
                            logger.error(f"Rate limit exceeded after {max_retries} retries")
                            raise
                    else:
                        # Re-raise non-rate-limit errors immediately
                        raise
            raise last_exception
        return wrapper
    return decorator


def handle_github_errors(func):
    """Decorator to handle GitHub API errors with logging."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except GithubException as e:
            logger.error(
                f"GitHub API error in {func.__name__}: {e.status} - {e.message}",
                exc_info=True
            )
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error in {func.__name__}: {e}",
                exc_info=True
            )
            raise
    return wrapper


def sanitize_label_name(name: str) -> str:
    """Sanitize a label name to be valid for GitHub.

    GitHub label rules:
    - Max 48 characters (limit raised to 255 but we keep it safe)
    - Cannot be empty
    - No leading/trailing whitespace
    - Allow: alphanumeric, hyphens, underscores, colons, spaces, dots
    """
    if not name or not name.strip():
        return "untitled"
    name = name.strip()
    # Replace disallowed characters with hyphens
    name = re.sub(r'[^a-zA-Z0-9_\-\:\.\s]', '-', name)
    # Collapse multiple hyphens/spaces
    name = re.sub(r'-{2,}', '-', name)
    name = re.sub(r'\s{2,}', ' ', name)
    # Trim to max 48 chars
    name = name[:48].rstrip('- ')
    return name or "untitled"


def ensure_labels_exist(repo: Repository.Repository, labels: List[str]) -> List[str]:
    """Ensure all labels exist in the repository, creating them if needed.

    Args:
        repo: PyGithub Repository object
        labels: List of label names to ensure exist

    Returns:
        Sanitized list of label names that now exist in the repo
    """
    if not labels:
        return []

    sanitized = [sanitize_label_name(l) for l in labels]
    # De-duplicate
    sanitized = list(dict.fromkeys(sanitized))

    # Fetch existing labels (cached for the call)
    try:
        existing = {label.name for label in repo.get_labels()}
    except Exception as e:
        logger.warning(f"Could not fetch existing labels: {e}")
        existing = set()

    for label_name in sanitized:
        if label_name not in existing:
            try:
                repo.create_label(name=label_name, color="ededed")
                logger.info(f"Created label '{label_name}' in repository")
                existing.add(label_name)
            except GithubException as e:
                if e.status == 422:
                    # Label already exists (race condition)
                    logger.debug(f"Label '{label_name}' already exists (422)")
                    existing.add(label_name)
                else:
                    logger.warning(f"Could not create label '{label_name}': {e}")

    return sanitized


class GitHubClient:
    """Client for GitHub API operations with error handling and retry logic."""

    def __init__(self):
        """Initialize GitHub client with token from settings."""
        self.client = Github(settings.github_token)
        self._repo: Optional[Repository.Repository] = None

    @property
    def repo(self) -> Repository.Repository:
        """Get the repository instance."""
        if self._repo is None:
            try:
                self._repo = self.client.get_repo(settings.github_repo)
            except GithubException as e:
                logger.error(f"Failed to get repository '{settings.github_repo}': {e}")
                raise
        return self._repo

    # ===========================================
    # Issue Operations
    # ===========================================

    @handle_github_errors
    @retry_on_rate_limit(max_retries=3)
    def get_issue(self, issue_number: int) -> Issue.Issue:
        """Get an issue by number."""
        logger.debug(f"Fetching issue #{issue_number}")
        return self.repo.get_issue(issue_number)

    @handle_github_errors
    @retry_on_rate_limit(max_retries=3)
    def create_issue(
        self,
        title: str,
        body: str,
        labels: Optional[List[str]] = None,
        assignees: Optional[List[str]] = None,
    ) -> Issue.Issue:
        """Create a new issue."""
        logger.info(f"Creating issue: {title}")
        # Ensure labels exist before creating the issue
        safe_labels = ensure_labels_exist(self.repo, labels or [])
        return self.repo.create_issue(
            title=title,
            body=body,
            labels=safe_labels,
            assignees=assignees or [],
        )

    @handle_github_errors
    @retry_on_rate_limit(max_retries=3)
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
        logger.info(f"Updating issue #{issue_number}")
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
        
        if kwargs:
            issue.edit(**kwargs)
            # Re-fetch to get updated state
            return self.get_issue(issue_number)
        return issue

    @handle_github_errors
    @retry_on_rate_limit(max_retries=3)
    def add_label(self, issue_number: int, label: str) -> None:
        """Add a label to an issue."""
        safe_label = sanitize_label_name(label)
        logger.info(f"Adding label '{safe_label}' to issue #{issue_number}")
        ensure_labels_exist(self.repo, [safe_label])
        issue = self.get_issue(issue_number)
        issue.add_to_labels(safe_label)

    @handle_github_errors
    @retry_on_rate_limit(max_retries=3)
    def remove_label(self, issue_number: int, label: str) -> None:
        """Remove a label from an issue."""
        logger.info(f"Removing label '{label}' from issue #{issue_number}")
        issue = self.get_issue(issue_number)
        issue.remove_from_labels(label)

    @handle_github_errors
    @retry_on_rate_limit(max_retries=3)
    def list_issues(
        self,
        state: str = "open",
        labels: Optional[List[str]] = None,
        limit: int = 100,
    ) -> List[Issue.Issue]:
        """List issues in the repository."""
        logger.debug(f"Listing issues (state={state}, labels={labels}, limit={limit})")
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
        logger.info(f"Found {len(result)} issues")
        return result

    # ===========================================
    # File Operations
    # ===========================================

    @handle_github_errors
    @retry_on_rate_limit(max_retries=3)
    def get_file(self, path: str, branch: str = "main") -> ContentFile:
        """Get file content from repository."""
        logger.debug(f"Fetching file '{path}' from branch '{branch}'")
        return self.repo.get_contents(path, ref=branch)

    @handle_github_errors
    @retry_on_rate_limit(max_retries=3)
    def create_file(
        self,
        path: str,
        content: str,
        message: str,
        branch: str = "main",
    ) -> dict:
        """Create a new file in the repository."""
        logger.info(f"Creating file '{path}' on branch '{branch}'")
        return self.repo.create_file(
            path=path,
            message=message,
            content=content,
            branch=branch,
        )

    @handle_github_errors
    @retry_on_rate_limit(max_retries=3)
    def update_file(
        self,
        path: str,
        content: str,
        message: str,
        branch: str = "main",
    ) -> dict:
        """Update an existing file."""
        logger.info(f"Updating file '{path}' on branch '{branch}'")
        file = self.get_file(path, branch)
        return self.repo.update_file(
            path=path,
            message=message,
            content=content,
            sha=file.sha,
            branch=branch,
        )

    @handle_github_errors
    @retry_on_rate_limit(max_retries=3)
    def delete_file(
        self,
        path: str,
        message: str,
        branch: str = "main",
    ) -> dict:
        """Delete a file from the repository."""
        logger.info(f"Deleting file '{path}' from branch '{branch}'")
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

    @handle_github_errors
    @retry_on_rate_limit(max_retries=3)
    @handle_github_errors
    @retry_on_rate_limit(max_retries=3)
    def create_branch(self, branch_name: str, base_branch: str = "main") -> str:
        """Create a new branch."""
        logger.info(f"Creating branch '{branch_name}' from '{base_branch}'")
        ref = self.repo.get_git_ref(f"heads/{base_branch}")
        self.repo.create_git_ref(f"refs/heads/{branch_name}", sha=ref.object.sha)
        return branch_name

    @handle_github_errors
    @retry_on_rate_limit(max_retries=3)
    def get_branch(self, branch_name: str):
        """Get a branch."""
        logger.debug(f"Fetching branch '{branch_name}'")
        return self.repo.get_branch(branch_name)

    @handle_github_errors
    @retry_on_rate_limit(max_retries=3)
    @handle_github_errors
    @retry_on_rate_limit(max_retries=3)
    def delete_branch(self, branch_name: str) -> None:
        """Delete a branch."""
        logger.info(f"Deleting branch '{branch_name}'")
        ref = self.repo.get_git_ref(f"heads/{branch_name}")
        ref.delete()

    # ===========================================
    # Pull Request Operations
    # ===========================================

    @handle_github_errors
    @retry_on_rate_limit(max_retries=3)
    def create_pull_request(
        self,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str = "main",
    ):
        """Create a pull request."""
        logger.info(f"Creating PR: {title} ({head_branch} -> {base_branch})")
        return self.repo.create_pull(
            title=title,
            body=body,
            head=head_branch,
            base=base_branch,
        )

    @handle_github_errors
    @retry_on_rate_limit(max_retries=3)
    @handle_github_errors
    @retry_on_rate_limit(max_retries=3)
    def get_pull_request(self, pr_number: int):
        """Get a pull request by number."""
        logger.debug(f"Fetching PR #{pr_number}")
        return self.repo.get_pull(pr_number)

    @handle_github_errors
    @retry_on_rate_limit(max_retries=3)
    def list_pull_requests(self, state: str = "open", limit: int = 100):
        """List pull requests."""
        logger.debug(f"Listing PRs (state={state}, limit={limit})")
        prs = self.repo.get_pulls(state=state)
        result = []
        for i, pr in enumerate(prs):
            if i >= limit:
                break
            result.append(pr)
        logger.info(f"Found {len(result)} PRs")
        return result

    @handle_github_errors
    @retry_on_rate_limit(max_retries=3)
    @handle_github_errors
    @retry_on_rate_limit(max_retries=3)
    def merge_pull_request(self, pr_number: int) -> bool:
        """Merge a pull request."""
        logger.info(f"Merging PR #{pr_number}")
        pr = self.get_pull_request(pr_number)
        pr.merge()
        return True


def get_github_client() -> GitHubClient:
    """Factory function to get a GitHub client instance.
    
    Use this for dependency injection instead of global instance.
    Creates a new instance each time (stateless client).
    """
    return GitHubClient()


# Global client instance (DEPRECATED: use get_github_client() instead)
github_client = GitHubClient()
