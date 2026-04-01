#!/usr/bin/env python3
"""
Cleanup artifacts before a new pipeline run.

Removes old artifacts to prevent confusion and ensure clean state.
Preserves state files by default.
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Directories to clean (relative to artifacts base)
CLEANUP_DIRS: List[str] = [
    "docs",
]

# Files to preserve (relative to artifacts base)
PRESERVE_PATTERNS: List[str] = [
    ".gitkeep",
    "README.md",
]

# State directory (never clean by default)
STATE_DIR = "state"


def cleanup_artifacts(
    base_path: Path,
    preserve_state: bool = True,
    dry_run: bool = False,
) -> int:
    """Clean up old artifacts.

    Args:
        base_path: Base artifacts directory
        preserve_state: If True, preserve state directory
        dry_run: If True, only print what would be deleted

    Returns:
        Number of files/directories removed
    """
    removed_count = 0

    if not base_path.exists():
        logger.warning(f"Base path does not exist: {base_path}")
        return 0

    # Clean artifact directories
    for dir_name in CLEANUP_DIRS:
        dir_path = base_path / dir_name

        if not dir_path.exists():
            continue

        # Check for files to preserve
        for item in dir_path.rglob("*"):
            if item.is_file():
                rel_path = item.relative_to(base_path)

                # Check preserve patterns
                should_preserve = any(
                    fnmatch.fnmatch(str(rel_path), pattern) or
                    item.name == pattern
                    for pattern in PRESERVE_PATTERNS
                )

                if should_preserve:
                    logger.info(f"Preserving: {rel_path}")
                    continue

                if dry_run:
                    logger.info(f"[DRY RUN] Would remove: {rel_path}")
                else:
                    item.unlink()
                    logger.debug(f"Removed: {rel_path}")
                removed_count += 1

        # Remove empty directories
        for item in sorted(dir_path.rglob("*"), reverse=True):
            if item.is_dir() and not any(item.iterdir()):
                if dry_run:
                    logger.info(f"[DRY RUN] Would remove empty dir: {item.relative_to(base_path)}")
                else:
                    item.rmdir()
                    logger.debug(f"Removed empty dir: {item.relative_to(base_path)}")
                removed_count += 1

    # Optionally clean state
    if not preserve_state:
        state_path = base_path / STATE_DIR
        if state_path.exists():
            if dry_run:
                logger.info(f"[DRY RUN] Would remove state directory: {state_path}")
            else:
                shutil.rmtree(state_path)
                state_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Reset state directory: {state_path}")
            removed_count += 1

    return removed_count


def create_clean_structure(base_path: Path, dry_run: bool = False) -> None:
    """Create clean directory structure.

    Args:
        base_path: Base artifacts directory
        dry_run: If True, only print what would be created
    """
    # Create directory structure aligned with file_permissions.py
    directories = [
        "docs/requirements",
        "docs/design/ui/screens",
        "docs/adr",
        "docs/tests",
        "docs/test-reports",
        "state",
    ]

    for dir_path in directories:
        full_path = base_path / dir_path
        if not full_path.exists():
            if dry_run:
                logger.info(f"[DRY RUN] Would create: {full_path}")
            else:
                full_path.mkdir(parents=True, exist_ok=True)
                # Create .gitkeep to preserve directory
                (full_path / ".gitkeep").touch()
                logger.info(f"Created: {full_path}")


def main():
    import argparse
    import fnmatch

    parser = argparse.ArgumentParser(description="Cleanup artifacts before pipeline run")
    parser.add_argument(
        "--base-path",
        type=Path,
        default=Path("data/artifacts"),
        help="Base artifacts directory",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually perform cleanup (default is dry-run)",
    )
    parser.add_argument(
        "--clean-state",
        action="store_true",
        help="Also clean state directory (resets pipeline state)",
    )
    parser.add_argument(
        "--create-structure",
        action="store_true",
        help="Create clean directory structure after cleanup",
    )

    args = parser.parse_args()

    logger.info(f"Cleaning artifacts in: {args.base_path}")
    logger.info(f"Mode: {'DRY RUN' if not args.execute else 'EXECUTING'}")
    logger.info("")

    # Perform cleanup
    removed = cleanup_artifacts(
        args.base_path,
        preserve_state=not args.clean_state,
        dry_run=not args.execute,
    )

    logger.info(f"\nTotal items {'would be ' if not args.execute else ''}removed: {removed}")

    # Create structure if requested
    if args.create_structure:
        logger.info("\nCreating directory structure...")
        create_clean_structure(args.base_path, dry_run=not args.execute)


if __name__ == "__main__":
    main()
