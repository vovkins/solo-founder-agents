"""CrewAI-compatible tools for artifact management."""

import logging
from typing import Optional, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from .artifact_manager import ArtifactManager, ArtifactType, get_artifact_manager
from .file_permissions import (
    check_file_permission,
    get_current_role,
    set_current_role,
    get_role_file_info,
    format_permissions_for_prompt,
)

logger = logging.getLogger(__name__)

# Re-export set_current_role and get_current_role from file_permissions
# (thread-local, not global — this is the SINGLE source of truth)
# Crew runners should import from here or from file_permissions directly.


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

        # Determine file path based on agreed directory structure:
        # artifacts/
        #   requirements/  → PRD, backlog, personas
        #   design/        → system-design, design-system, ui/
        #   adr/           → Architecture Decision Records
        #   implementation/ → PRs, branches, commits
        #   tests/         → Unit, integration
        from datetime import datetime
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        
        if artifact_type_enum == ArtifactType.PRD:
            filepath = "docs/requirements/prd.md"
        elif artifact_type_enum == ArtifactType.SYSTEM_DESIGN:
            filepath = "docs/design/system-design.md"
        elif artifact_type_enum == ArtifactType.ADR:
            filepath = f"docs/adr/{name or timestamp}.md"
        elif artifact_type_enum == ArtifactType.DESIGN_SYSTEM:
            filepath = "docs/design/design-system.md"
        elif artifact_type_enum == ArtifactType.UI_SCREEN:
            filepath = f"docs/design/ui/screens/{name or timestamp}.md"
        elif artifact_type_enum == ArtifactType.USER_FLOW:
            filepath = f"docs/design/ui/flows/{name or timestamp}.md"
        elif artifact_type_enum == ArtifactType.TEST_CASE:
            filepath = f"docs/tests/{name or timestamp}-test-case.md"
        elif artifact_type_enum == ArtifactType.TEST_RUN_LOG:
            filepath = f"docs/tests/{name or timestamp}-run-log.md"
        else:
            filepath = f"docs/{name or timestamp}.md"

        # Save artifact (permission check is now in artifact_manager.save_artifact)
        artifact = self.artifact_manager.create_artifact(
            artifact_type=artifact_type_enum,
            content=content,
            name=name,
        )
        try:
            url = self.artifact_manager.save_artifact(artifact)
            return f"✅ Artifact saved to: {url}"
        except PermissionError as e:
            return f"⛔ {e}"


class ReadArtifactInput(BaseModel):
    """Input schema for ReadArtifactTool."""

    path: str = Field(..., description="Path to the artifact in the repository (e.g., 'docs/prd.md')")


class ReadArtifactTool(BaseTool):
    """Tool for reading artifacts from GitHub.

    Use this tool when you need to read an existing document or artifact
    from the GitHub repository.

    Example:
        read_artifact("docs/requirements/prd.md")
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


class ListMyFilesInput(BaseModel):
    """Input schema for ListMyFilesTool."""
    pass


class ListMyFilesTool(BaseTool):
    """Show which files the current agent can create/modify.

    Use this tool to check your file permissions before saving artifacts.
    """

    name: str = "list_my_files"
    description: str = "Show which files you can create and modify. Always use this if unsure about permissions."
    args_schema: Type[BaseModel] = ListMyFilesInput

    def _run(self) -> str:
        """Return file permissions for the current role.

        Returns:
            Human-readable list of allowed files
        """
        role = get_current_role()
        if not role:
            return "⚠️ No role set. Call set_current_role() first."

        perms = get_role_file_info(role)
        lines = [f"📋 Your permissions as '{role}':\n"]

        if perms["can_create"]:
            lines.append("✅ You CAN create/edit:")
            for path in perms["can_create"]:
                lines.append(f"   • {path}")
        else:
            lines.append("❌ You cannot create or edit any files.")

        if perms.get("read_only"):
            lines.append("\n📖 You can READ (but NOT modify):")
            for path in perms["read_only"]:
                lines.append(f"   • {path}")

        return "\n".join(lines)


def get_artifact_tools() -> list:
    """Get full artifact tools for agents that can create/edit files.

    Includes: SaveArtifactTool, ReadArtifactTool, ListMyFilesTool.
    Does NOT include SyncArtifactsTool (bypasses permissions).
    """
    return [SaveArtifactTool(), ReadArtifactTool(), ListMyFilesTool()]


def get_readonly_artifact_tools() -> list:
    """Get read-only artifact tools for agents that cannot create files.

    Includes: ReadArtifactTool, ListMyFilesTool only.
    """
    return [ReadArtifactTool(), ListMyFilesTool()]
