"""CrewAI-compatible tools for artifact management."""

import logging
from typing import Optional, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from .artifact_manager import ArtifactManager, ArtifactType, get_artifact_manager
from .file_permissions import check_file_permission

logger = logging.getLogger(__name__)

# Current role context (set by crew before running)
_current_role: str = "developer"


def set_current_role(role: str) -> None:
    """Set the current role for permission checks."""
    global _current_role
    _current_role = role
    logger.debug(f"Current role set to: {role}")


def get_current_role() -> str:
    """Get the current role for permission checks."""
    return _current_role


class SaveArtifactInput(BaseModel):
    """Input schema for SaveArtifactTool."""

    artifact_type: str = Field(
        ...,
        description="Type of artifact: prd, system-design, adr, design-system, ui-screen, user-flow, test-case, test-run-log",
    )
    content: str = Field(..., description="Content of the artifact in Markdown format")
    name: Optional[str] = Field(None, description="Optional name for the artifact (used in filename)")


class SaveArtifactTool(BaseTool):
    """Tool for saving artifacts to GitHub.

    Use this tool when you need to save a document or artifact that should
    be persisted in the GitHub repository.

    Example:
        save_artifact("design-system", "# Design System\\n\\n...")
    """

    name: str = "save_artifact"
    description: str = "Save an artifact to the GitHub repository. Use this to persist documents like PRD, design system, ADRs, etc."
    args_schema: Type[BaseModel] = SaveArtifactInput

    artifact_manager: ArtifactManager = Field(default_factory=get_artifact_manager)

    def _run(
        self,
        artifact_type: str,
        content: str,
        name: Optional[str] = None,
    ) -> str:
        """Save artifact to GitHub.

        Args:
            artifact_type: Type of artifact
            content: Artifact content
            name: Optional name

        Returns:
            URL to the artifact
        """
        # Map string to enum
        type_map = {
            "prd": ArtifactType.PRD,
            "system-design": ArtifactType.SYSTEM_DESIGN,
            "adr": ArtifactType.ADR,
            "design-system": ArtifactType.DESIGN_SYSTEM,
            "ui-screen": ArtifactType.UI_SCREEN,
            "user-flow": ArtifactType.USER_FLOW,
            "test-case": ArtifactType.TEST_CASE,
            "test-run-log": ArtifactType.TEST_RUN_LOG,
        }

        if artifact_type not in type_map:
            return f"Error: Unknown artifact type '{artifact_type}'. Valid types: {list(type_map.keys())}"

        artifact_type_enum = type_map[artifact_type]

        # Determine file path for permission check (same logic as artifact_manager)
        from datetime import datetime
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        
        if artifact_type_enum == ArtifactType.PRD:
            filepath = "docs/prd.md"
        elif artifact_type_enum == ArtifactType.SYSTEM_DESIGN:
            filepath = "docs/system-design.md"
        elif artifact_type_enum == ArtifactType.ADR:
            filepath = f"docs/adr/{name or timestamp}.md"
        elif artifact_type_enum == ArtifactType.DESIGN_SYSTEM:
            filepath = "docs/design-system.md"
        elif artifact_type_enum == ArtifactType.UI_SCREEN:
            filepath = f"docs/ui/screens/{name or timestamp}.md"
        elif artifact_type_enum == ArtifactType.USER_FLOW:
            filepath = f"docs/user-flows/{name or timestamp}.md"
        elif artifact_type_enum == ArtifactType.TEST_CASE:
            filepath = f"docs/tests/{name or timestamp}-test-case.md"
        elif artifact_type_enum == ArtifactType.TEST_RUN_LOG:
            filepath = f"docs/tests/{name or timestamp}-run-log.md"
        else:
            filepath = f"docs/{name or timestamp}.md"

        # Check permissions
        role = get_current_role()
        if role:
            allowed = check_file_permission(role, filepath, "create")
            if not allowed:
                logger.warning(f"Permission denied for {role} on {filepath}")
                return f"⚠️ Permission denied for {role} on {filepath}\n\nPlease create files only in your designated directories."

        # Save artifact
        artifact = self.artifact_manager.create_artifact(
            artifact_type=artifact_type_enum,
            content=content,
            name=name,
        )
        url = self.artifact_manager.save_artifact(artifact)
        return f"✅ Artifact saved to: {url}"


class ReadArtifactInput(BaseModel):
    """Input schema for ReadArtifactTool."""

    path: str = Field(..., description="Path to the artifact in the repository (e.g., 'docs/prd.md')")


class ReadArtifactTool(BaseTool):
    """Tool for reading artifacts from GitHub.

    Use this tool when you need to read an existing document or artifact
    from the GitHub repository.

    Example:
        read_artifact("docs/prd.md")
    """

    name: str = "read_artifact"
    description: str = "Read an artifact from the GitHub repository. Use this to read existing documents."
    args_schema: Type[BaseModel] = ReadArtifactInput

    artifact_manager: ArtifactManager = Field(default_factory=get_artifact_manager)

    def _run(self, path: str) -> str:
        """Read artifact from GitHub.

        Args:
            path: Artifact path

        Returns:
            Artifact content
        """
        try:
            return self.artifact_manager.read_artifact(path)
        except FileNotFoundError:
            return f"Error: Artifact not found at '{path}'"


class SyncArtifactsInput(BaseModel):
    """Input schema for SyncArtifactsTool."""

    pass


class SyncArtifactsTool(BaseTool):
    """Tool for syncing all local artifacts to GitHub.

    Use this tool when you want to ensure all local artifacts are
    synced to the GitHub repository.
    """

    name: str = "sync_artifacts"
    description: str = "Sync all local artifacts to GitHub. Use this to ensure all artifacts are backed up."
    args_schema: Type[BaseModel] = SyncArtifactsInput

    artifact_manager: ArtifactManager = Field(default_factory=get_artifact_manager)

    def _run(self) -> str:
        """Sync all artifacts to GitHub.

        Returns:
            Summary of sync results
        """
        results = self.artifact_manager.sync_all_to_github()
        return f"Synced {len(results['synced'])} artifacts. Errors: {len(results['errors'])}"


# Export tools for use in agents
ARTIFACT_TOOLS = [
    SaveArtifactTool(),
    ReadArtifactTool(),
    SyncArtifactsTool(),
]


def get_artifact_tools() -> list:
    """Get all artifact tools for use in agents."""
    return ARTIFACT_TOOLS
