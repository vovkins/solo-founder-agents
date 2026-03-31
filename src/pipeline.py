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
from src.crews import run_dev_crew
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
        """Run the requirements phase (PM + Analyst + Architect).

        Uses separate crews to avoid context overflow.

        Args:
            founder_vision: Founder's product vision

        Returns:
            Results from the phase
        """
        print("\n" + "=" * 50)
        print("📋 PHASE: Requirements")
        print("=" * 50)

        self.current_stage = PipelineStage.REQUIREMENTS
        results = {"artifacts": {}}

        # Step 1: PM Crew (requirements + PRD + backlog)
        print("\n--- Step 1/3: PM Crew ---")
        state_manager.update_agent_state("pm", "working", "collecting_requirements")
        from src.crews import run_pm_crew
        pm_result = run_pm_crew(founder_vision)
        results["artifacts"]["prd"] = pm_result.get("artifacts", {}).get("prd")
        self.state["prd_path"] = results["artifacts"]["prd"]
        state_manager.update_agent_state("pm", "idle")
        print("✅ PM Crew completed")

        # Step 2: Analyst Crew (feature decomposition + task specs)
        print("\n--- Step 2/3: Analyst Crew ---")
        state_manager.update_agent_state("analyst", "working", "decomposing_features")
        from src.crews import run_analyst_crew
        analyst_result = run_analyst_crew()
        results["artifacts"]["task_specs"] = analyst_result.get("artifacts", {}).get("task_specs")
        state_manager.update_agent_state("analyst", "idle")
        print("✅ Analyst Crew completed")

        # Step 3: Architect Crew (architecture + system design)
        print("\n--- Step 3/3: Architect Crew ---")
        state_manager.update_agent_state("architect", "working", "designing_architecture")
        from src.crews import run_architect_crew
        architect_result = run_architect_crew()
        results["artifacts"]["system_design"] = architect_result.get("artifacts", {}).get("system_design")
        results["artifacts"]["standards"] = architect_result.get("artifacts", {}).get("standards")
        state_manager.update_agent_state("architect", "idle")
        print("✅ Architect Crew completed")

        self.current_stage = PipelineStage.DESIGN
        results["status"] = "completed"

        return results

    def run_design_phase(self) -> dict:
        """Run the design phase (UI/UX).

        Returns:
            Results from the phase
        """
        print("\n" + "=" * 50)
        print("🎨 PHASE: Design")
        print("=" * 50)

        state_manager.update_agent_state("designer", "working", "creating_ui_specs")

        # Architecture is done in requirements phase (architect_crew)
        # Designer creates UI specs here (future: add designer_crew)

        state_manager.update_agent_state("designer", "idle")
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

    def run_full_pipeline(
        self,
        issue_number: int,
        founder_vision: str,
        on_checkpoint: Optional[Callable] = None,
        on_progress: Optional[Callable] = None,
    ) -> dict:
        """Run the full pipeline for a task.

        Args:
            issue_number: GitHub Issue number
            founder_vision: Founder's product vision (from PRD)
            on_checkpoint: Callback for checkpoint notifications
            on_progress: Callback for progress updates

        Returns:
            Final results
        """
        results = {"issue_number": issue_number, "phases": {}}

        try:
            # Phase 1: Requirements (if PRD not already created)
            if on_progress:
                on_progress("requirements", "Анализирую требования...")
            
            req_result = self.run_requirements_phase(founder_vision)
            results["phases"]["requirements"] = req_result

            # Checkpoint 1: PRD
            if on_checkpoint:
                on_checkpoint(Checkpoint.CHECKPOINT_1, ["docs/prd.md"])

            # Phase 2: Design
            if on_progress:
                on_progress("design", "Проектирую архитектуру...")
            
            design_result = self.run_design_phase()
            results["phases"]["design"] = design_result

            # Checkpoint 2: System Design
            if on_checkpoint:
                on_checkpoint(Checkpoint.CHECKPOINT_2, ["docs/system-design.md"])

            # Phase 3: Implementation
            if on_progress:
                on_progress("implementation", "Разрабатываю код...")
            
            impl_result = self.run_implementation_phase(issue_number)
            results["phases"]["implementation"] = impl_result

            pr_url = impl_result.get("pr_url")
            if pr_url:
                # Checkpoint 3: Implementation
                if on_checkpoint:
                    on_checkpoint(Checkpoint.CHECKPOINT_3, [pr_url])

                # Phase 4: QA
                if on_progress:
                    on_progress("qa", "Тестирую...")
                
                qa_result = self.run_qa_phase(pr_url)
                results["phases"]["qa"] = qa_result

                # Checkpoint 4: QA passed
                if on_checkpoint:
                    on_checkpoint(Checkpoint.CHECKPOINT_4, [pr_url])

            # Phase 5: Documentation
            if on_progress:
                on_progress("documentation", "Обновляю документацию...")
            
            doc_result = self.run_documentation_phase()
            results["phases"]["documentation"] = doc_result

            # Checkpoint 5: Complete
            if on_checkpoint:
                on_checkpoint(Checkpoint.CHECKPOINT_5, results.get("pr_urls", []))

            results["status"] = "complete"

        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)
            print(f"Pipeline error: {e}")

        return results


# Global pipeline instance
pipeline = Pipeline()
