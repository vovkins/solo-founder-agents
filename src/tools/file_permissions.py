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
            "docs/prd.md",
            "docs/backlog*.md",
            "docs/personas.md",
        ],
        "can_modify": [
            "docs/prd.md",
            "docs/backlog*.md",
        ],
        "read_only": [],
    },
    "analyst": {
        "can_create": [
            "docs/task-specs.md",
            "docs/dependency-map.md",
            "docs/feature-*.md",
        ],
        "can_modify": [
            "docs/task-specs.md",
            "docs/dependency-map.md",
            "docs/feature-*.md",
        ],
        "read_only": [
            "docs/prd.md",
            "docs/backlog*.md",
        ],
    },
    "architect": {
        "can_create": [
            "docs/system-design.md",
            "docs/standards.md",
            "docs/adr/*.md",
        ],
        "can_modify": [
            "docs/system-design.md",
            "docs/standards.md",
            "docs/adr/*.md",
        ],
        "read_only": [
            "docs/prd.md",
            "docs/backlog*.md",
        ],
    },
    "designer": {
        "can_create": [
            "docs/design-system.md",
            "docs/ui/**/*.md",
            "docs/screens/*.md",
        ],
        "can_modify": [
            "docs/design-system.md",
            "docs/ui/**/*.md",
        ],
        "read_only": [
            "docs/prd.md",
            "docs/system-design.md",
            "docs/standards.md",
        ],
    },
    "developer": {
        "can_create": [
            "src/**",
            "docs/tests/**/*.md",
            "docs/adr/pull-request-*.md",
            "docs/adr/branch-*.md",
            "docs/ui/screens/*.md",  # Can add implementation details to UI specs
        ],
        "can_modify": [
            "src/**",
            "docs/tests/**",
            "docs/adr/pull-request-*.md",
        ],
        "read_only": [
            "docs/prd.md",
            "docs/system-design.md",
            "docs/design-system.md",
            "docs/standards.md",
        ],
    },
    "qa": {
        "can_create": [
            "docs/tests/**/*.md",
            "docs/qa/**/*.md",
        ],
        "can_modify": [
            "docs/tests/**",
        ],
        "read_only": [
            "docs/prd.md",
            "docs/system-design.md",
            "src/**",
        ],
    },
    "reviewer": {
        "can_create": [
            "docs/reviews/**/*.md",
        ],
        "can_modify": [
            "docs/reviews/**",
        ],
        "read_only": [
            "docs/prd.md",
            "docs/system-design.md",
            "src/**",
        ],
    },
    "tech_writer": {
        "can_create": [
            "docs/**/*.md",  # Can create documentation anywhere
            "README.md",
        ],
        "can_modify": [
            "docs/**/*.md",
            "README.md",
        ],
        "read_only": [
            "src/**",  # Cannot modify code, only document it
        ],
    },
}


def matches_pattern(filepath: str, pattern: str) -> bool:
    """Check if filepath matches a glob pattern.
    
    Args:
        filepath: File path to check
        pattern: Glob pattern (e.g., "docs/**/*.md", "src/**")
    
    Returns:
        True if filepath matches pattern
    """
    # Normalize paths
    filepath = filepath.replace("\\", "/").lstrip("/")
    pattern = pattern.replace("\\", "/").lstrip("/")
    
    # Handle ** patterns
    if "**" in pattern:
        # Convert ** to a regex-like match
        # For simplicity, use fnmatch with path parts
        parts = pattern.split("**")
        if len(parts) == 2:
            prefix, suffix = parts
            prefix = prefix.rstrip("/")
            suffix = suffix.lstrip("/")
            
            # Check if filepath starts with prefix
            if prefix and not filepath.startswith(prefix):
                return False
            
            # Check if filepath ends with suffix pattern
            if suffix:
                # Extract the end part of filepath
                if "/" in filepath:
                    end_part = filepath[filepath.rfind("/") + 1:]
                else:
                    end_part = filepath
                
                return fnmatch.fnmatch(end_part, suffix) or fnmatch.fnmatch(filepath, "*" + suffix)
            
            return True
    
    # Simple fnmatch for non-** patterns
    return fnmatch.fnmatch(filepath, pattern)


def check_file_permission(
    role: str,
    filepath: str,
    action: str,
    file_exists: bool = True,
) -> tuple[bool, Optional[str]]:
    """Check if role can perform action on filepath.
    
    Args:
        role: Role name (pm, analyst, architect, designer, developer, qa, reviewer, tech_writer)
        filepath: File path to check
        action: Action to perform (read, create, modify, delete)
        file_exists: Whether the file already exists
    
    Returns:
        Tuple of (allowed: bool, reason: Optional[str])
    """
    # Normalize filepath
    filepath = filepath.replace("\\", "/").lstrip("/")
    
    # Get permissions for role
    perms = ROLE_FILE_PERMISSIONS.get(role.lower())
    if not perms:
        return False, f"Unknown role: {role}"
    
    # Read is always allowed (except for sensitive files)
    if action == "read":
        return True, None
    
    # Check read_only restriction first
    if action in ("modify", "delete"):
        for pattern in perms.get("read_only", []):
            if matches_pattern(filepath, pattern):
                return False, f"Role '{role}' cannot modify '{filepath}' - it's read-only for this role"
    
    # For create action
    if action == "create" or (action == "modify" and not file_exists):
        for pattern in perms.get("can_create", []):
            if matches_pattern(filepath, pattern):
                return True, None
        return False, f"Role '{role}' cannot create '{filepath}'"
    
    # For modify action (file exists)
    if action == "modify":
        # Check can_modify first
        for pattern in perms.get("can_modify", []):
            if matches_pattern(filepath, pattern):
                return True, None
        
        # Check can_create as fallback
        for pattern in perms.get("can_create", []):
            if matches_pattern(filepath, pattern):
                return True, None
        
        return False, f"Role '{role}' cannot modify '{filepath}'"
    
    # For delete action
    if action == "delete":
        # Only allow delete if can_create
        for pattern in perms.get("can_create", []):
            if matches_pattern(filepath, pattern):
                return True, None
        return False, f"Role '{role}' cannot delete '{filepath}'"
    
    return False, f"Unknown action: {action}"


def validate_artifact_path(role: str, filepath: str, action: str = "create") -> bool:
    """Validate and log artifact path access.
    
    Args:
        role: Role name
        filepath: File path to validate
        action: Action to perform
    
    Returns:
        True if allowed, False otherwise
    """
    allowed, reason = check_file_permission(role, filepath, action)
    
    if not allowed:
        logger.warning(f"Permission denied: {reason}")
    else:
        logger.debug(f"Permission granted: {role} can {action} {filepath}")
    
    return allowed


def get_role_for_crew(crew_name: str) -> str:
    """Get the primary role for a crew.
    
    Args:
        crew_name: Crew name (e.g., 'pm_crew', 'analyst_crew')
    
    Returns:
        Role name
    """
    CREW_ROLE_MAP = {
        "pm_crew": "pm",
        "analyst_crew": "analyst",
        "architect_crew": "architect",
        "designer_crew": "designer",
        "dev_crew": "developer",
        "qa_crew": "qa",
        "reviewer_crew": "reviewer",
        "tech_writer_crew": "tech_writer",
    }
    
    return CREW_ROLE_MAP.get(crew_name, crew_name.replace("_crew", ""))
