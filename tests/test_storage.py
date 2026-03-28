"""Tests for storage utilities."""

import pytest
from pathlib import Path
import tempfile
import os

from src.tools.storage import (
    save_artifact,
    load_artifact,
    artifact_exists,
    list_artifacts,
)


class TestStorage:
    """Tests for storage utilities."""

    def test_save_and_load_artifact(self, tmp_path):
        """Test saving and loading an artifact."""
        # Use temp directory
        with tempfile.TemporaryDirectory() as tmpdir:
            import src.tools.storage as storage
            original_dir = storage.ARTIFACTS_DIR
            storage.ARTIFACTS_DIR = Path(tmpdir) / "artifacts"

            try:
                # Save artifact
                path = save_artifact(
                    "test.md",
                    "# Test Content\n\nThis is a test.",
                    "docs",
                )

                assert "test.md" in path
                assert artifact_exists("test.md", "docs")

                # Load artifact
                content = load_artifact("test.md", "docs")
                assert "# Test Content" in content
            finally:
                storage.ARTIFACTS_DIR = original_dir

    def test_list_artifacts(self, tmp_path):
        """Test listing artifacts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import src.tools.storage as storage
            original_dir = storage.ARTIFACTS_DIR
            storage.ARTIFACTS_DIR = Path(tmpdir) / "artifacts"

            try:
                # Save multiple artifacts
                save_artifact("test1.md", "Content 1", "docs")
                save_artifact("test2.md", "Content 2", "docs")

                # List artifacts
                artifacts = list_artifacts("docs")
                assert len(artifacts) == 2
            finally:
                storage.ARTIFACTS_DIR = original_dir


class TestState:
    """Tests for state management."""

    def test_task_status(self, tmp_path):
        """Test setting and getting task status."""
        from src.tools.state import StateManager

        with tempfile.TemporaryDirectory() as tmpdir:
            import src.tools.state as state
            original_dir = state.STATE_DIR
            state.STATE_DIR = Path(tmpdir) / "state"
            state.STATE_FILE = state.STATE_DIR / "state.json"

            try:
                manager = StateManager()

                # Set status
                manager.set_task_status("task-1", "in_progress", {"title": "Test Task"})

                # Get status
                status = manager.get_task_status("task-1")
                assert status == "in_progress"

                # Get details
                details = manager.get_task_details("task-1")
                assert details["title"] == "Test Task"
            finally:
                state.STATE_DIR = original_dir
                state.STATE_FILE = state.STATE_DIR / "state.json"

    def test_checkpoint(self, tmp_path):
        """Test checkpoint management."""
        from src.tools.state import StateManager

        with tempfile.TemporaryDirectory() as tmpdir:
            import src.tools.state as state
            original_dir = state.STATE_DIR
            state.STATE_DIR = Path(tmpdir) / "state"
            state.STATE_FILE = state.STATE_DIR / "state.json"

            try:
                manager = StateManager()

                # Set checkpoint
                manager.set_checkpoint(
                    "checkpoint_1",
                    "pending_review",
                    ["docs/prd.md"],
                )

                # Get checkpoint
                cp = manager.get_checkpoint("checkpoint_1")
                assert cp["status"] == "pending_review"
                assert "docs/prd.md" in cp["artifacts"]

                # Approve
                manager.approve_checkpoint("checkpoint_1", "LGTM")
                cp = manager.get_checkpoint("checkpoint_1")
                assert cp["status"] == "approved"
            finally:
                state.STATE_DIR = original_dir
                state.STATE_FILE = state.STATE_DIR / "state.json"
