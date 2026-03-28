"""Tests for pipeline orchestration."""

import pytest
from unittest.mock import Mock, patch

from src.pipeline import Pipeline, PipelineStage, Checkpoint


class TestPipeline:
    """Tests for Pipeline orchestration."""

    def test_initial_state(self):
        """Test pipeline initial state."""
        pipeline = Pipeline(verbose=False)

        assert pipeline.current_stage == PipelineStage.REQUIREMENTS
        assert pipeline.state["prd_path"] is None
        assert pipeline.state["pr_urls"] == []

    def test_get_status(self):
        """Test getting pipeline status."""
        pipeline = Pipeline(verbose=False)

        status = pipeline.get_status()

        assert "current_stage" in status
        assert "state" in status
        assert status["current_stage"] == PipelineStage.REQUIREMENTS.value

    def test_is_complete(self):
        """Test completion check."""
        pipeline = Pipeline(verbose=False)

        assert not pipeline.is_complete()

        pipeline.current_stage = PipelineStage.COMPLETE
        assert pipeline.is_complete()


class TestCheckpoints:
    """Tests for checkpoint management."""

    def test_checkpoint_enum(self):
        """Test checkpoint enum values."""
        assert Checkpoint.CHECKPOINT_1.value == "checkpoint_1"
        assert Checkpoint.CHECKPOINT_5.value == "checkpoint_5"

    def test_pipeline_stage_enum(self):
        """Test pipeline stage enum values."""
        assert PipelineStage.REQUIREMENTS.value == "requirements"
        assert PipelineStage.IMPLEMENTATION.value == "implementation"
        assert PipelineStage.COMPLETE.value == "complete"
