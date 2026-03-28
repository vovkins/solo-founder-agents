"""Storage utilities for artifacts and documents."""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional


# Base directory for all data
DATA_DIR = Path("data")
ARTIFACTS_DIR = DATA_DIR / "artifacts"


def ensure_dir(path: Path) -> None:
    """Ensure directory exists.

    Args:
        path: Directory path
    """
    path.mkdir(parents=True, exist_ok=True)


def save_artifact(
    filename: str,
    content: str,
    artifact_type: str = "docs",
    frontmatter: Optional[dict] = None,
) -> str:
    """Save an artifact as a Markdown file.

    Args:
        filename: Name of the file (e.g., 'prd.md')
        content: Markdown content
        artifact_type: Type/category of artifact (e.g., 'docs', 'adr')
        frontmatter: Optional YAML frontmatter

    Returns:
        Path to the saved file
    """
    # Create artifact directory
    artifact_dir = ARTIFACTS_DIR / artifact_type
    ensure_dir(artifact_dir)

    # Build file path
    file_path = artifact_dir / filename

    # Build frontmatter
    if frontmatter is None:
        frontmatter = {}

    frontmatter.setdefault("created", datetime.now().isoformat())
    frontmatter.setdefault("type", artifact_type)

    # Format frontmatter
    frontmatter_str = "---\n"
    for key, value in frontmatter.items():
        frontmatter_str += f"{key}: {value}\n"
    frontmatter_str += "---\n\n"

    # Write file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(frontmatter_str + content)

    return str(file_path)


def load_artifact(filename: str, artifact_type: str = "docs") -> str:
    """Load an artifact from a Markdown file.

    Args:
        filename: Name of the file
        artifact_type: Type/category of artifact

    Returns:
        File content (without frontmatter)
    """
    file_path = ARTIFACTS_DIR / artifact_type / filename

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Strip frontmatter if present
    if content.startswith("---\n"):
        parts = content.split("---\n", 2)
        if len(parts) >= 3:
            return parts[2].strip()

    return content


def load_artifact_raw(filename: str, artifact_type: str = "docs") -> str:
    """Load an artifact including frontmatter.

    Args:
        filename: Name of the file
        artifact_type: Type/category of artifact

    Returns:
        Full file content including frontmatter
    """
    file_path = ARTIFACTS_DIR / artifact_type / filename

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def artifact_exists(filename: str, artifact_type: str = "docs") -> bool:
    """Check if an artifact exists.

    Args:
        filename: Name of the file
        artifact_type: Type/category of artifact

    Returns:
        True if file exists
    """
    file_path = ARTIFACTS_DIR / artifact_type / filename
    return file_path.exists()


def list_artifacts(artifact_type: Optional[str] = None) -> list[str]:
    """List all artifacts, optionally filtered by type.

    Args:
        artifact_type: Type/category to filter by (optional)

    Returns:
        List of artifact paths
    """
    artifacts = []

    if artifact_type:
        # List specific type
        type_dir = ARTIFACTS_DIR / artifact_type
        if type_dir.exists():
            artifacts = [str(f) for f in type_dir.glob("*.md")]
    else:
        # List all types
        if ARTIFACTS_DIR.exists():
            for type_dir in ARTIFACTS_DIR.iterdir():
                if type_dir.is_dir():
                    artifacts.extend(str(f) for f in type_dir.glob("*.md"))

    return artifacts


def delete_artifact(filename: str, artifact_type: str = "docs") -> bool:
    """Delete an artifact.

    Args:
        filename: Name of the file
        artifact_type: Type/category of artifact

    Returns:
        True if deleted successfully
    """
    file_path = ARTIFACTS_DIR / artifact_type / filename

    if file_path.exists():
        file_path.unlink()
        return True

    return False
