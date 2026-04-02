"""File permission system for role-based artifact access control.

Three-level protection:
1. System prompt — agent knows rights at start
2. list_my_files() tool — agent can check when unsure
3. save_artifact() check — hard block if writes to wrong file

All levels use this single source of truth: ROLE_FILE_PERMISSIONS
"""

import fnmatch
import threading
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# ROLE FILE PERMISSIONS — Single Source of Truth
# =============================================================================
# Every role defines:
#   can_create  — files this role can create (new files)
#   can_modify  — files this role can edit (existing files)
#   read_only   — files from other roles (read but NEVER write)
#
# Wildcards: * matches any single path segment, ** matches any depth
# =============================================================================

ROLE_FILE_PERMISSIONS: Dict[str, Dict[str, List[str]]] = {
    "pm": {
        "can_create": [
            "docs/requirements/prd.md",
            "docs/requirements/backlog.md",
            "docs/requirements/personas.md",
        ],
        "can_modify": [
            "docs/requirements/prd.md",
            "docs/requirements/backlog.md",
            "docs/requirements/personas.md",
        ],
        "read_only": [
            "docs/design/**",
            "docs/adr/**",
            "docs/tests/**",
            "docs/implementation/**",
        ],
    },
    "analyst": {
        "can_create": [
            "docs/requirements/task-specs.md",
            "docs/requirements/dep-map.md",
            "docs/requirements/feature-*.md",
        ],
        "can_modify": [
            "docs/requirements/task-specs.md",
            "docs/requirements/dep-map.md",
            "docs/requirements/feature-*.md",
        ],
        "read_only": [
            "docs/requirements/prd.md",
            "docs/requirements/backlog.md",
            "docs/design/**",
            "docs/adr/**",
            "docs/tests/**",
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
            "docs/requirements/**",
            "docs/design/design-system.md",
            "docs/design/ui/**",
            "docs/tests/**",
        ],
    },
    "designer": {
        "can_create": [
            "docs/design/design-system.md",
            "docs/design/ui/screens/*.md",
            "docs/design/ui/flows/*.md",
            "docs/design/ui/components/*.md",
        ],
        "can_modify": [
            "docs/design/design-system.md",
            "docs/design/ui/screens/*.md",
            "docs/design/ui/flows/*.md",
            "docs/design/ui/components/*.md",
        ],
        "read_only": [
            "docs/requirements/**",
            "docs/design/system-design.md",
            "docs/design/standards.md",
            "docs/adr/**",
        ],
    },
    "developer": {
        "can_create": [
            "docs/implementation/pull-request-*.md",
            "docs/implementation/branch-*.md",
            "docs/tests/*-test-case.md",
            "src/**",
        ],
        "can_modify": [
            "docs/implementation/**",
            "docs/tests/*-test-case.md",
            "src/**",
        ],
        "read_only": [
            "docs/requirements/**",
            "docs/design/**",
            "docs/adr/**",
        ],
    },
    "qa": {
        "can_create": [
            "docs/tests/*-test-case.md",
            "docs/tests/*-run-log.md",
            "docs/tests/qa-signoff-*.md",
        ],
        "can_modify": [
            "docs/tests/*-test-case.md",
            "docs/tests/*-run-log.md",
            "docs/tests/qa-signoff-*.md",
        ],
        "read_only": [
            "docs/requirements/**",
            "docs/design/**",
            "docs/adr/**",
            "src/**",
        ],
    },
    "reviewer": {
        "can_create": [],
        "can_modify": [],
        "read_only": [
            "docs/**",
            "src/**",
        ],
    },
    "tech_writer": {
        "can_create": [
            "docs/user-guide.md",
            "docs/api-docs.md",
            "docs/changelog.md",
        ],
        "can_modify": [
            "docs/user-guide.md",
            "docs/api-docs.md",
            "docs/changelog.md",
            "README.md",
        ],
        "read_only": [
            "docs/requirements/**",
            "docs/design/**",
            "docs/adr/**",
            "docs/tests/**",
            "src/**",
        ],
    },
    # Special role for core_crew which runs PM + Analyst + Architect together
    "core_crew": {
        "can_create": [
            # PM permissions
            "docs/requirements/prd.md",
            "docs/requirements/backlog.md",
            "docs/requirements/personas.md",
            # Analyst permissions
            "docs/requirements/task-specs.md",
            "docs/requirements/dep-map.md",
            "docs/requirements/feature-*.md",
            # Architect permissions
            "docs/design/system-design.md",
            "docs/design/standards.md",
            "docs/adr/*.md",
        ],
        "can_modify": [
            # PM
            "docs/requirements/prd.md",
            "docs/requirements/backlog.md",
            "docs/requirements/personas.md",
            # Analyst
            "docs/requirements/task-specs.md",
            "docs/requirements/dep-map.md",
            "docs/requirements/feature-*.md",
            # Architect
            "docs/design/system-design.md",
            "docs/design/standards.md",
            "docs/adr/*.md",
        ],
        "read_only": [
            "docs/tests/**",
            "src/**",
        ],
    },
}


# =============================================================================
# Pattern Matching
# =============================================================================

def matches_pattern(filepath: str, pattern: str) -> bool:
    """Check if filepath matches a permission pattern.

    Supports:
      *      — any single path segment (e.g., docs/*.md)
      **     — any depth (e.g., docs/**/*.md)
      feature-*  — prefix matching within segment
    """
    if "**" in pattern:
        parts = pattern.split("**")
        if len(parts) == 2:
            prefix, suffix = parts
            if filepath.startswith(prefix):
                remaining = filepath[len(prefix):]
                return fnmatch.fnmatch(remaining, suffix) or remaining.endswith(suffix.rstrip("*"))
        return False
    return fnmatch.fnmatch(filepath, pattern)


# =============================================================================
# Permission Checks
# =============================================================================

def check_file_permission(role: str, filepath: str, action: str = "create") -> bool:
    """Check if a role has permission for an action on a file.

    Args:
        role: Role name (pm, analyst, architect, etc.)
        filepath: File path relative to artifacts directory
        action: "create", "modify", or "read"

    Returns:
        True if permission granted, False otherwise
    """
    if role not in ROLE_FILE_PERMISSIONS:
        logger.warning(f"Unknown role: {role}")
        return False

    permissions = ROLE_FILE_PERMISSIONS[role]
    filepath = filepath.lstrip("/")

    if action == "read":
        # All roles can read everything
        return True

    if action == "create":
        patterns = permissions.get("can_create", [])
    elif action == "modify":
        patterns = permissions.get("can_modify", []) + permissions.get("can_create", [])
    else:
        return False

    for pattern in patterns:
        if matches_pattern(filepath, pattern):
            return True

    logger.warning(f"Permission denied: {role} cannot {action} {filepath}")
    return False


def get_role_file_info(role: str) -> dict:
    """Get file permission info for a role (for system prompts and tools).

    Returns dict with can_create, can_modify, read_only lists.
    """
    return ROLE_FILE_PERMISSIONS.get(role, {
        "can_create": [],
        "can_modify": [],
        "read_only": [],
    })


def format_permissions_for_prompt(role: str) -> str:
    """Format permissions as human-readable text for system prompts."""
    perms = get_role_file_info(role)
    if not perms["can_create"] and not perms["can_modify"]:
        return "У тебя нет прав на создание или редактирование файлов."

    lines = []
    if perms["can_create"]:
        lines.append("Файлы, которые ты МОЖЕШЬ создавать и редактировать:")
        for path in perms["can_create"]:
            lines.append(f"  - {path}")
    if perms.get("read_only"):
        lines.append("\nФайлы, которые ты можешь ТОЛЬКО ЧИТАТЬ (НЕ перезаписывать!):")
        for path in perms["read_only"]:
            lines.append(f"  - {path}")
    lines.append("\nВАЖНО: НЕ пытайся писать в файлы, которые тебе не принадлежат!")

    return "\n".join(lines)


# =============================================================================
# Thread-Local Role Context
# =============================================================================

_current_role = threading.local()


def set_current_role(role: str) -> None:
    """Set the current role for the running thread."""
    _current_role.value = role
    logger.info(f"Role context set to: {role}")


def get_current_role() -> Optional[str]:
    """Get the current role for the running thread."""
    return getattr(_current_role, "value", None)


def check_current_role_permission(filepath: str, action: str = "create") -> bool:
    """Check permission using the current thread's role context."""
    role = get_current_role()
    if not role:
        logger.warning("No role context set, denying permission")
        return False
    return check_file_permission(role, filepath, action)
