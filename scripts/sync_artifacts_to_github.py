#!/usr/bin/env python3
"""Sync artifacts from local filesystem to GitHub repository."""

import os
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.github_tools import create_file_in_repo, read_file_from_repo


def sync_artifacts_to_github(artifacts_dir: str = "data/artifacts", branch: str = "main") -> dict:
    """Sync all artifacts from local directory to GitHub.
    
    Args:
        artifacts_dir: Local directory with artifacts
        branch: GitHub branch to push to
        
    Returns:
        Dictionary with sync results
    """
    results = {
        "synced": [],
        "skipped": [],
        "errors": [],
    }
    
    artifacts_path = Path(artifacts_dir)
    
    if not artifacts_path.exists():
        print(f"❌ Artifacts directory not found: {artifacts_dir}")
        return results
    
    # Find all markdown and json files
    for ext in ["*.md", "*.json", "*.yaml", "*.yml"]:
        for file_path in artifacts_path.rglob(ext):
            relative_path = file_path.relative_to(artifacts_path)
            github_path = str(relative_path)
            
            try:
                # Read local file
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Check if file already exists in GitHub
                try:
                    existing = read_file_from_repo(github_path, branch)
                    # File exists, update it
                    url = create_file_in_repo(
                        path=github_path,
                        content=content,
                        message=f"Update {github_path}",
                        branch=branch,
                    )
                    results["synced"].append({
                        "path": github_path,
                        "action": "updated",
                        "url": url,
                    })
                    print(f"✅ Updated: {github_path}")
                except Exception:
                    # File doesn't exist, create it
                    url = create_file_in_repo(
                        path=github_path,
                        content=content,
                        message=f"Create {github_path}",
                        branch=branch,
                    )
                    results["synced"].append({
                        "path": github_path,
                        "action": "created",
                        "url": url,
                    })
                    print(f"✅ Created: {github_path}")
                    
            except Exception as e:
                results["errors"].append({
                    "path": github_path,
                    "error": str(e),
                })
                print(f"❌ Error syncing {github_path}: {e}")
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Sync artifacts to GitHub")
    parser.add_argument(
        "--dir",
        default="data/artifacts",
        help="Local artifacts directory",
    )
    parser.add_argument(
        "--branch",
        default="main",
        help="GitHub branch",
    )
    
    args = parser.parse_args()
    
    print(f"🚀 Syncing artifacts from {args.dir} to GitHub...")
    results = sync_artifacts_to_github(args.dir, args.branch)
    
    print(f"\n📊 Results:")
    print(f"  Synced: {len(results['synced'])}")
    print(f"  Skipped: {len(results['skipped'])}")
    print(f"  Errors: {len(results['errors'])}")
