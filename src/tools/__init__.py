"""Tools for CrewAI agents."""

from .github_client import GitHubClient, github_client
from .github_tools import (
    create_github_issue,
    update_github_issue,
    add_label_to_issue,
    close_issue,
    get_issue_details,
    list_open_issues,
    read_file_from_repo,
    create_file_in_repo,
    update_file_in_repo,
    create_pull_request,
    CreateGitHubIssueTool,
    ListOpenIssuesTool,
    CreatePullRequestTool,
)
from .state import StateManager, state_manager
from .artifact_manager import ArtifactManager, ArtifactType, get_artifact_manager
from .artifact_tools import (
    SaveArtifactTool,
    ReadArtifactTool,
    SyncArtifactsTool,
    get_artifact_tools,
    get_readonly_artifact_tools,
)


def get_github_tools():
    """Get GitHub tools for CrewAI agents."""
    return [
        CreateGitHubIssueTool(),
        CreatePullRequestTool(),
        ListOpenIssuesTool(),
    ]


__all__ = [
    "GitHubClient",
    "github_client",
    "create_github_issue",
    "update_github_issue",
    "add_label_to_issue",
    "close_issue",
    "get_issue_details",
    "list_open_issues",
    "read_file_from_repo",
    "create_file_in_repo",
    "update_file_in_repo",
    "create_pull_request",
    "StateManager",
    "state_manager",
    "ArtifactManager",
    "ArtifactType",
    "get_artifact_manager",
    "SaveArtifactTool",
    "ReadArtifactTool",
    "SyncArtifactsTool",
    "get_artifact_tools",
    "get_readonly_artifact_tools",
    "CreateGitHubIssueTool",
    "ListOpenIssuesTool",
    "CreatePullRequestTool",
    "get_github_tools",
]
