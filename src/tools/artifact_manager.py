"""Artifact Manager for syncing artifacts to GitHub."""

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from .github_tools import create_file_in_repo, read_file_from_repo, update_file_in_repo

logger = logging.getLogger(__name__)


class ArtifactType(Enum):
    """Types of artifacts."""

    PRD = "prd"
    SYSTEM_DESIGN = "system-design"
    ADR = "adr"
    DESIGN_SYSTEM = "design-system"
    UI_SCREEN = "ui-screen"
    USER_FLOW = "user-flow"
    TEST_CASE = "test-case"
    TEST_RUN_LOG = "test-run-log"
    PR = "pull-request"
    GITHUB_ISSUE = "github-issue"


@dataclass
class Artifact:
    """Represents an artifact."""

    type: ArtifactType
    path: str  # Relative path in repo
    content: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.type.value,
            "path": self.path,
            "content": self.content[:200] + "..." if len(self.content) > 200 else self.content,
            "metadata": self.metadata,
        }


class ArtifactManager:
    """Manages artifacts and syncs them to GitHub.

    This class provides a unified interface for:
    1. Storing artifacts locally (for development/testing)
    2. Syncing artifacts to GitHub (for production)
    3. Reading artifacts from GitHub
    4. Tracking artifact history

    Usage:
        manager = ArtifactManager()

        # Save artifact
        artifact = Artifact(
            type=ArtifactType.PRD,
            path="docs/requirements/prd.md",
            content="# PRD Content...",
            metadata={"version": "1.0"}
        )
        url = manager.save_artifact(artifact)

        # Read artifact
        content = manager.read_artifact("docs/requirements/prd.md")

        # List artifacts
        artifacts = manager.list_artifacts(ArtifactType.DESIGN_SYSTEM)
    """

    def __init__(
        self,
        local_dir: str = "data/artifacts",
        github_sync: bool = True,
        branch: str = settings.github_default_branch,
    ):
        """Initialize ArtifactManager.

        Args:
            local_dir: Local directory for artifacts
            github_sync: Whether to sync to GitHub
            branch: GitHub branch to sync to
        """
        self.local_dir = Path(local_dir)
        self.github_sync = github_sync
        self.branch = branch
        self._ensure_local_dir()

    def _ensure_local_dir(self) -> None:
        """Ensure local directory exists."""
        self.local_dir.mkdir(parents=True, exist_ok=True)

    def save_artifact(
        self,
        artifact: Artifact,
        commit_message: Optional[str] = None,
    ) -> str:
        """Save artifact to local storage and optionally to GitHub.

        Centralized save point with permission check (Level 3 protection).

        Args:
            artifact: Artifact to save
            commit_message: Custom commit message (optional)

        Returns:
            URL to the artifact in GitHub or local path

        Raises:
            PermissionError: If current role cannot write to this path
        """
        # === PERMISSION CHECK (Level 3: Hard block) ===
        from .file_permissions import get_current_role, check_current_role_permission
        role = get_current_role()
        logger.info(f"[PERMISSION CHECK] role={role}, path={artifact.path}, action=create")
        if role is None:
            logger.error(
                f"BLOCKED: No role context set — tried to write to '{artifact.path}'. "
                f"File NOT saved. Call set_current_role() before saving artifacts."
            )
            raise PermissionError(
                f"No role context set. Cannot write to '{artifact.path}'. "
                f"The crew runner must call set_current_role() before saving."
            )
        if not check_current_role_permission(artifact.path, "create"):
            logger.error(
                f"BLOCKED: Role '{role}' tried to write to '{artifact.path}' — "
                f"permission denied. File NOT saved."
            )
            raise PermissionError(
                f"Role '{role}' cannot write to '{artifact.path}'. "
                f"Check your permissions with list_my_files tool."
            )
        logger.info(f"[PERMISSION GRANTED] role={role} → {artifact.path}")

        # Save locally
        local_path = self.local_dir / artifact.path
        local_path.parent.mkdir(parents=True, exist_ok=True)
        local_path.write_text(artifact.content, encoding="utf-8")

        # Add metadata
        metadata_path = local_path.with_suffix(".meta.json")
        metadata = {
            **artifact.metadata,
            "type": artifact.type.value,
            "created_at": datetime.utcnow().isoformat(),
            "local_path": str(local_path),
        }
        metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

        # Sync to GitHub if enabled
        if self.github_sync:
            message = commit_message or f"docs: Update {artifact.path}"
            try:
                # Check if file exists (catch only file-not-found, not all errors)
                existing_content = None
                try:
                    existing_content = read_file_from_repo(artifact.path, self.branch)
                except FileNotFoundError:
                    pass  # File doesn't exist yet — will create below
                except Exception as e:
                    # Log unexpected error but don't silently fall through to create
                    logger.warning(f"Unexpected error reading {artifact.path}: {e}")

                if existing_content is not None:
                    url = update_file_in_repo(
                        path=artifact.path,
                        content=artifact.content,
                        message=message,
                        branch=self.branch,
                    )
                else:
                    url = create_file_in_repo(
                        path=artifact.path,
                        content=artifact.content,
                        message=message,
                        branch=self.branch,
                    )
                return url
            except Exception as e:
                logger.warning(f"Failed to sync to GitHub: {e}")
                return str(local_path)

        return str(local_path)

    def read_artifact(self, path: str) -> str:
        """Read artifact content.

        Args:
            path: Artifact path

        Returns:
            Artifact content
        """
        # Try GitHub first if sync enabled
        if self.github_sync:
            try:
                return read_file_from_repo(path, self.branch)
            except Exception:
                pass

        # Fall back to local
        local_path = self.local_dir / path
        if local_path.exists():
            return local_path.read_text(encoding="utf-8")

        raise FileNotFoundError(f"Artifact not found: {path}")

    def list_artifacts(
        self,
        artifact_type: Optional[ArtifactType] = None,
    ) -> List[Dict[str, Any]]:
        """List all artifacts, optionally filtered by type.

        Args:
            artifact_type: Filter by type (optional)

        Returns:
            List of artifact info dictionaries
        """
        artifacts = []

        for meta_file in self.local_dir.rglob("*.meta.json"):
            try:
                metadata = json.loads(meta_file.read_text(encoding="utf-8"))
                artifact_info = {
                    "type": metadata.get("type"),
                    "path": str(meta_file.with_suffix("").relative_to(self.local_dir)),
                    "created_at": metadata.get("created_at"),
                    "metadata": metadata,
                }

                if artifact_type is None or artifact_info["type"] == artifact_type.value:
                    artifacts.append(artifact_info)
            except Exception:
                continue

        return sorted(artifacts, key=lambda x: x.get("created_at", ""), reverse=True)

    def sync_all_to_github(self) -> Dict[str, Any]:
        """Sync all local artifacts to GitHub.

        Returns:
            Summary of sync results
        """
        results = {"synced": [], "errors": []}

        for content_file in self.local_dir.rglob("*.md"):
            relative_path = str(content_file.relative_to(self.local_dir))

            try:
                content = content_file.read_text(encoding="utf-8")
                message = f"docs: Sync {relative_path}"

                try:
                    read_file_from_repo(relative_path, self.branch)
                    url = update_file_in_repo(relative_path, content, message, self.branch)
                except Exception:
                    url = create_file_in_repo(relative_path, content, message, self.branch)

                results["synced"].append({"path": relative_path, "url": url})
            except Exception as e:
                results["errors"].append({"path": relative_path, "error": str(e)})

        return results

    def create_artifact(
        self,
        artifact_type: ArtifactType,
        content: str,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Artifact:
        """Create an artifact with auto-generated path.

        Args:
            artifact_type: Type of artifact
            content: Artifact content
            name: Optional name (used in path)
            metadata: Optional metadata

        Returns:
            Created Artifact instance
        """
        # Generate path based on type
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")

        if artifact_type == ArtifactType.PRD:
            path = "docs/requirements/prd.md"
        elif artifact_type == ArtifactType.SYSTEM_DESIGN:
            path = "docs/design/system-design.md"
        elif artifact_type == ArtifactType.ADR:
            path = f"docs/adr/{name or timestamp}.md"
        elif artifact_type == ArtifactType.DESIGN_SYSTEM:
            path = "docs/design/design-system.md"
        elif artifact_type == ArtifactType.UI_SCREEN:
            path = f"docs/design/ui/screens/{name or timestamp}.md"
        elif artifact_type == ArtifactType.USER_FLOW:
            path = f"docs/design/ui/flows/{name or timestamp}.md"
        elif artifact_type == ArtifactType.TEST_CASE:
            path = f"docs/tests/{name or timestamp}-test-case.md"
        elif artifact_type == ArtifactType.TEST_RUN_LOG:
            path = f"docs/tests/{name or timestamp}-run-log.md"
        else:
            path = f"docs/{name or timestamp}.md"

        return Artifact(
            type=artifact_type,
            path=path,
            content=content,
            metadata=metadata or {},
        )


# Global instance for convenience
_artifact_manager: Optional[ArtifactManager] = None


def get_artifact_manager() -> ArtifactManager:
    """Get or create the global ArtifactManager instance."""
    global _artifact_manager
    if _artifact_manager is None:
        _artifact_manager = ArtifactManager()
    return _artifact_manager
