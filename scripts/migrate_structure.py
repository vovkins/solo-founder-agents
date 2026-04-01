#!/usr/bin/env python3
"""
Migrate artifact directory structure to role-based organization.

Old structure:
  docs/prd.md, backlog.md → docs/requirements/
  docs/system-design.md, design-system.md → docs/design/
  docs/adr/ → docs/adr/
  docs/ui/, docs/screens/ → docs/design/ui/
  docs/tests/ → docs/tests/

New structure aligns with file_permissions.py roles.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Migration map: (old_pattern, new_dir)
MIGRATIONS: List[Tuple[str, str]] = [
    # Requirements (PM + Analyst)
    ("docs/prd.md", "docs/requirements/prd.md"),
    ("docs/backlog*.md", "docs/requirements/backlog.md"),
    ("docs/personas.md", "docs/requirements/personas.md"),
    ("docs/task-specs.md", "docs/requirements/task-specs.md"),
    ("docs/dependency-map.md", "docs/requirements/dependency-map.md"),
    ("docs/feature-*.md", "docs/requirements/"),

    # Design (Architect + Designer)
    ("docs/system-design.md", "docs/design/system-design.md"),
    ("docs/design-system.md", "docs/design/design-system.md"),
    ("docs/standards.md", "docs/design/standards.md"),
    ("docs/ui/", "docs/design/ui/"),
    ("docs/screens/", "docs/design/ui/screens/"),

    # ADR stays in place
    # Tests stay in place
]


def migrate_artifacts(base_path: Path, dry_run: bool = True) -> None:
    """Migrate artifacts to new structure.

    Args:
        base_path: Base directory (e.g., data/artifacts)
        dry_run: If True, only print what would happen
    """
    docs_path = base_path / "docs"

    if not docs_path.exists():
        logger.warning(f"docs/ directory not found: {docs_path}")
        return

    # Create new directories
    new_dirs = [
        "docs/requirements",
        "docs/design",
        "docs/design/ui",
        "docs/design/ui/screens",
    ]

    for dir_path in new_dirs:
        full_path = base_path / dir_path
        if not full_path.exists():
            if dry_run:
                logger.info(f"[DRY RUN] Would create: {full_path}")
            else:
                full_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created: {full_path}")

    # Migrate files
    for old_pattern, new_path in MIGRATIONS:
        # Handle directories
        if old_pattern.endswith("/"):
            old_dir = docs_path / old_pattern.rstrip("/")
            new_dir = base_path / new_path.rstrip("/")

            if old_dir.exists() and old_dir.is_dir():
                if dry_run:
                    logger.info(f"[DRY RUN] Would move: {old_dir} → {new_dir}")
                else:
                    if new_dir.exists():
                        shutil.rmtree(new_dir)
                    shutil.move(str(old_dir), str(new_dir))
                    logger.info(f"Moved: {old_dir} → {new_dir}")
            continue

        # Handle files with patterns
        if "*" in old_pattern:
            import glob
            matches = list((docs_path).glob(old_pattern.replace("docs/", "")))
            for old_file in matches:
                if new_path.endswith("/"):
                    # Keep filename
                    new_file = base_path / new_path / old_file.name
                else:
                    new_file = base_path / new_path

                if old_file.exists():
                    if dry_run:
                        logger.info(f"[DRY RUN] Would move: {old_file} → {new_file}")
                    else:
                        new_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(old_file), str(new_file))
                        logger.info(f"Moved: {old_file} → {new_file}")
        else:
            # Single file
            old_file = base_path / old_pattern
            new_file = base_path / new_path

            if old_file.exists():
                if dry_run:
                    logger.info(f"[DRY RUN] Would move: {old_file} → {new_file}")
                else:
                    new_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(old_file), str(new_file))
                    logger.info(f"Moved: {old_file} → {new_file}")

    logger.info(f"\nMigration {'simulated' if dry_run else 'complete'}!")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Migrate artifact structure")
    parser.add_argument(
        "--base-path",
        type=Path,
        default=Path("data/artifacts"),
        help="Base artifacts directory",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually perform migration (default is dry-run)",
    )

    args = parser.parse_args()

    migrate_artifacts(args.base_path, dry_run=not args.execute)


if __name__ == "__main__":
    main()
