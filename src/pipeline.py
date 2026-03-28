"""Pipeline orchestration for running agents in sequence."""

from enum import Enum
from typing import Optional, Callable

from src.agents import (
    pm_agent,
    analyst_agent,
    architect_agent,
    designer_agent,
    developer_agent,
    reviewer_agent,
    qa_agent,
    tech_writer_agent,
)
from src.crews import run_core_crew, run_dev_crew
from src.tools.state import state_manager


class PipelineStage(str, Enum):
    """Pipeline execution stages."""

    REQUIREMENTS = "requirements"
    DESIGN = "design"
    IMPLEMENTATION = "implementation"
    REVIEW = "review"
    QA = "qa"
    DOCUMENTATION = "documentation"
    COMPLETE = "complete"


class Checkpoint(str, Enum):
    """Founder review checkpoints."""

    CHECKPOINT_1 = "checkpoint_1"  # After PRD
    CHECKPOINT_2 = "checkpoint_2"  # After System Design
    CHECKPOINT_3 = "checkpoint_3"  # After Implementation
    CHECKPOINT_4 = "checkpoint_4"  # After QA
    CHECKPOINT_5 = "checkpoint_5"  # Final Release


class Pipeline:
    """Pipeline orchestrator for agent execution."""

    def __init__(self, verbose: bool = True):
        """Initialize the pipeline.

        Args:
            verbose: Whether to show detailed output
        """
        self.verbose = verbose
        self.current_stage = PipelineStage.REQUIREMENTS
        self.state = {
            "prd_path": None,
            "system_design_path": None,
            "task_issues": [],
            "pr_urls": [],
            "qa_status": None,
        }

    def run_requirements_phase(self, founder_vision: str) -> dict:
        """Run the requirements phase (PM + Analyst).

        Args:
            founder_vision: Founder's product vision

        Returns:
            Results from the phase
        """
        print("\n" + "=" * 50)
        print("📋 PHASE: Requirements")
        print("=" * 50)

        self.current_stage = PipelineStage.REQUIREMENTS
        state_manager.update_agent_state("pm", "working", "collecting_requirements")

        # Run core crew for requirements
        result = run_core_crew(founder_vision)

        self.state["prd_path"] = result.get("artifacts", {}).get("prd")

        state_manager.update_agent_state("pm", "idle")
        self.current_stage = PipelineStage.DESIGN

        return result

    def run_design_phase(self) -> dict:
        """Run the design phase (Architect + Designer).

        Returns:
            Results from the phase
        """
        print("\n" + "=" * 50)
        print("🎨 PHASE: Design")
        print("=" * 50)

        state_manager.update_agent_state("architect", "working", "creating_design")

        # Architecture is done in core_crew
        # Designer creates UI specs here

        state_manager.update_agent_state("architect", "idle")
        self.current_stage = PipelineStage.IMPLEMENTATION

        return {"status": "design_complete"}

    def run_implementation_phase(self, issue_number: int) -> dict:
        """Run implementation phase for a single task.

        Args:
            issue_number: GitHub Issue number for the task

        Returns:
            Results from the phase
        """
        print("\n" + "=" * 50)
        print(f"💻 PHASE: Implementation (Issue #{issue_number})")
        print("=" * 50)

        self.current_stage = PipelineStage.IMPLEMENTATION

        # Get issue details
        from src.tools import get_issue_details

        issue = get_issue_details(issue_number)

        # Run dev crew
        result = run_dev_crew(issue_number, issue.get("title", ""))

        self.state["pr_urls"].append(result.get("pr_url"))

        self.current_stage = PipelineStage.REVIEW

        return result

    def run_review_phase(self, pr_url: str) -> dict:
        """Run the review phase.

        Args:
            pr_url: Pull Request URL to review

        Returns:
            Review results
        """
        print("\n" + "=" * 50)
        print("👀 PHASE: Review")
        print("=" * 50)

        self.current_stage = PipelineStage.REVIEW
        state_manager.update_agent_state("reviewer", "working", f"reviewing_{pr_url}")

        # Review is handled by dev_crew
        # This is for manual re-review if needed

        state_manager.update_agent_state("reviewer", "idle")
        self.current_stage = PipelineStage.QA

        return {"status": "review_complete", "pr_url": pr_url}

    def run_qa_phase(self, pr_url: str) -> dict:
        """Run the QA phase.

        Args:
            pr_url: Pull Request URL to test

        Returns:
            QA results
        """
        print("\n" + "=" * 50)
        print("✅ PHASE: QA")
        print("=" * 50)

        self.current_stage = PipelineStage.QA
        state_manager.update_agent_state("qa", "working", f"testing_{pr_url}")

        # QA is handled by dev_crew
        # This is for manual re-testing if needed

        state_manager.update_agent_state("qa", "idle")
        self.state["qa_status"] = "passed"

        self.current_stage = PipelineStage.DOCUMENTATION

        return {"status": "qa_complete", "pr_url": pr_url}

    def run_documentation_phase(self) -> dict:
        """Run the documentation phase.

        Returns:
            Documentation results
        """
        print("\n" + "=" * 50)
        print("📝 PHASE: Documentation")
        print("=" * 50)

        self.current_stage = PipelineStage.DOCUMENTATION
        state_manager.update_agent_state("tech_writer", "working", "updating_docs")

        # Tech writer updates docs

        state_manager.update_agent_state("tech_writer", "idle")
        self.current_stage = PipelineStage.COMPLETE

        return {"status": "documentation_complete"}

    def request_checkpoint(self, checkpoint: Checkpoint, artifacts: list) -> dict:
        """Request founder review at a checkpoint.

        Args:
            checkpoint: Which checkpoint
            artifacts: List of artifacts to review

        Returns:
            Checkpoint status
        """
        print("\n" + "=" * 50)
        print(f"🛑 CHECKPOINT: {checkpoint.value}")
        print("=" * 50)
        print("Artifacts for review:")
        for artifact in artifacts:
            print(f"  - {artifact}")
        print("\nWaiting for founder approval...")

        state_manager.set_checkpoint(
            checkpoint.value,
            "pending_review",
            artifacts,
        )

        return {"status": "pending_review", "checkpoint": checkpoint.value}

    def approve_checkpoint(self, checkpoint: Checkpoint, notes: str = "") -> None:
        """Approve a checkpoint.

        Args:
            checkpoint: Which checkpoint to approve
            notes: Optional approval notes
        """
        state_manager.approve_checkpoint(checkpoint.value, notes)
        print(f"\n✅ Checkpoint {checkpoint.value} approved!")

    def reject_checkpoint(self, checkpoint: Checkpoint, reason: str) -> None:
        """Reject a checkpoint.

        Args:
            checkpoint: Which checkpoint to reject
            reason: Reason for rejection
        """
        state_manager.reject_checkpoint(checkpoint.value, reason)
        print(f"\n❌ Checkpoint {checkpoint.value} rejected: {reason}")

    def get_status(self) -> dict:
        """Get current pipeline status.

        Returns:
            Status dictionary
        """
        return {
            "current_stage": self.current_stage.value,
            "state": self.state,
            "agents": state_manager.state.get("agents", {}),
        }

    def is_complete(self) -> bool:
        """Check if pipeline is complete.

        Returns:
            True if complete
        """
        return self.current_stage == PipelineStage.COMPLETE


# Global pipeline instance
pipeline = Pipeline()
