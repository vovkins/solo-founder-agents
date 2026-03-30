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
)
from .storage import (
    save_artifact,
    load_artifact,
    load_artifact_raw,
    artifact_exists,
    list_artifacts,
    delete_artifact,
)
from .state import StateManager, state_manager
from .artifact_manager import ArtifactManager, ArtifactType, get_artifact_manager
from .artifact_tools import (
    SaveArtifactTool,
    ReadArtifactTool,
    SyncArtifactsTool,
    get_artifact_tools,
)

__all__ = [
    # GitHub Client
    "GitHubClient",
    "github_client",
    # Issue Tools
    "create_github_issue",
    "update_github_issue",
    "add_label_to_issue",
    "close_issue",
    "get_issue_details",
    "list_open_issues",
    # File Tools
    "read_file_from_repo",
    "create_file_in_repo",
    "update_file_in_repo",
    # Pull Request Tools
    "create_pull_request",
    # Storage
    "save_artifact",
    "load_artifact",
    "load_artifact_raw",
    "artifact_exists",
    "list_artifacts",
    "delete_artifact",
    # State
    "StateManager",
    "state_manager",
    # Artifact Manager
    "ArtifactManager",
    "ArtifactType",
    "get_artifact_manager",
    # Artifact Tools
    "SaveArtifactTool",
    "ReadArtifactTool",
    "SyncArtifactsTool",
    "get_artifact_tools",
]
