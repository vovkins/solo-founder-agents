"""File permission system for role-based artifact access control."""

import fnmatch
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


# Role-based file permissions
# Each role can:
# - can_create: Create new files matching these patterns
# - can_modify: Modify files matching these patterns
# - read_only: Can only read these files (cannot modify)
ROLE_FILE_PERMISSIONS: Dict[str, Dict[str, List[str]]] = {
    "pm": {
        "can_create": [
            "docs/requirements/prd.md",
            "docs/requirements/backlog*.md",
            "docs/requirements/personas.md",
            "docs/prd.md",
            "docs/backlog*.md",
        ],
        "can_modify": [
            "docs/requirements/prd.md",
            "docs/requirements/backlog*.md",
            "docs/prd.md",
            "docs/backlog*.md",
        ],
        "read_only": [],
    },
    "analyst": {
        "can_create": [
            "docs/requirements/task-specs.md",
            "docs/requirements/dependency-map.md",
            "docs/requirements/feature-*.md",
        ],
        "can_modify": [
            "docs/requirements/task-specs.md",
            "docs/requirements/dependency-map.md",
            "docs/requirements/feature-*.md",
        ],
        "read_only": [
            "docs/requirements/prd.md",
            "docs/requirements/backlog*.md",
        ],
    },
    "architect": {
        "can_create": [
            "docs/design/system-design.md",
            "docs/design/standards.md",
            "docs/adr/*.md",
        ],
        "can_modify": [
            "docs/design/system-design.md",
            "docs/design/standards.md",
            "docs/adr/*.md",
        ],
        "read_only": [
            "docs/requirements/prd.md",
            "docs/requirements/task-specs.md",
        ],
    },
    "designer": {
        "can_create": [
            "docs/design/design-system.md",
            "docs/design/ui/**/*.md",
        ],
        "can_modify": [
            "docs/design/design-system.md",
            "docs/design/ui/**/*.md",
        ],
        "read_only": [
            "docs/requirements/prd.md",
            "docs/design/system-design.md",
            "docs/design/standards.md",
        ],
    },
    "developer": {
        "can_create": [
            "src/**",
            "docs/tests/**/*.md",
            "docs/adr/pull-request-*.md",
        ],
        "can_modify": [
            "src/**",
            "docs/tests/**/*.md",
        ],
        "read_only": [
            "docs/requirements/**",
            "docs/design/**",
            "docs/adr/*.md",
        ],
    },
    "qa": {
        "can_create": [
            "docs/tests/**/*.md",
            "docs/test-reports/**/*.md",
        ],
        "can_modify": [
            "docs/tests/**/*.md",
            "docs/test-reports/**/*.md",
        ],
        "read_only": [
            "docs/requirements/**",
            "docs/design/**",
            "src/**",
        ],
    },
    "reviewer": {
        "can_create": [],
        "can_modify": [],
        "read_only": [
            "src/**",
            "docs/**",
        ],
    },
    "tech_writer": {
        "can_create": [
            "docs/README.md",
            "docs/user-guide.md",
            "docs/api-docs.md",
        ],
        "can_modify": [
            "docs/README.md",
            "docs/user-guide.md",
            "docs/api-docs.md",
        ],
        "read_only": [
            "docs/**",
            "src/**",
        ],
    },
}


def matches_pattern(filename: str, pattern: str) -> bool:
    """Check if filename matches a pattern with wildcards.

    Args:
        filename: File path to check
        pattern: Pattern with wildcards (e.g., "docs/requirements/*.md")

    Returns:
        True if matches, False otherwise
    """
    # Handle ** for recursive matching
    if "**" in pattern:
        # Convert ** to match any path
        parts = pattern.split("**")
        if len(parts) == 2:
            prefix, suffix = parts
            if filename.startswith(prefix):
                remaining = filename[len(prefix):]
                # Suffix should match the end
                return remaining.endswith(suffix.rstrip("*")) or fnmatch.fnmatch(remaining, suffix)
        return False

    # Simple wildcard matching
    return fnmatch.fnmatch(filename, pattern)


def check_file_permission(
    role: str,
    filepath: str,
    action: str = "create",
) -> bool:
    """Check if a role has permission to perform an action on a file.

    Args:
        role: Role name (pm, analyst, architect, etc.)
        filepath: File path relative to artifacts directory
        action: Action to check (create, modify, read)

    Returns:
        True if permission granted, False otherwise
    """
    if role not in ROLE_FILE_PERMISSIONS:
        logger.warning(f"Unknown role: {role}")
        return False

    permissions = ROLE_FILE_PERMISSIONS[role]

    # Normalize path
    filepath = filepath.lstrip("/")

    if action == "read":
        # All roles can read their read_only files
        for pattern in permissions.get("read_only", []):
            if matches_pattern(filepath, pattern):
                return True
        # Also check if they can create/modify (implies read)
        for pattern in permissions.get("can_create", []) + permissions.get("can_modify", []):
            if matches_pattern(filepath, pattern):
                return True
        return False

    if action == "create":
        patterns = permissions.get("can_create", [])
    elif action == "modify":
        # Can modify if in can_modify OR can_create (new files can be created then modified)
        patterns = permissions.get("can_modify", []) + permissions.get("can_create", [])
    else:
        logger.warning(f"Unknown action: {action}")
        return False

    for pattern in patterns:
        if matches_pattern(filepath, pattern):
            logger.debug(f"Permission granted: {role} can {action} {filepath}")
            return True

    logger.warning(f"Permission denied: {role} cannot {action} {filepath}")
    return False


# Current role context (thread-local storage)
import threading

_current_role = threading.local()


def set_current_role(role: str) -> None:
    """Set the current role for permission checks.

    Args:
        role: Role name to set
    """
    _current_role.value = role
    logger.debug(f"Current role set to: {role}")


def get_current_role() -> Optional[str]:
    """Get the current role for permission checks.

    Returns:
        Current role name or None if not set
    """
    return getattr(_current_role, "value", None)


def check_current_role_permission(filepath: str, action: str = "create") -> bool:
    """Check permission using the current role context.

    Args:
        filepath: File path to check
        action: Action to check

    Returns:
        True if permission granted, False otherwise
    """
    role = get_current_role()
    if not role:
        logger.warning("No role context set, denying permission")
        return False
    return check_file_permission(role, filepath, action)
