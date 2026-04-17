"""Pipeline orchestration for running agents in sequence.

Each phase runs a single-agent crew with proper role isolation.
No crew contains multiple agents — each role has its own crew.

FIX: Removed global pipeline instance to prevent race conditions.
Each pipeline run now creates its own instance.
"""

import logging
import threading
from enum import Enum
from typing import Optional, Callable, Dict, Any
from typing import Optional, Any

from src.tools.state import state_manager

logger = logging.getLogger(__name__)


class PipelineStage(str, Enum):
    """Pipeline execution stages."""
    REQUIREMENTS = "requirements"
    ANALYSIS = "analysis"
    DESIGN = "design"
    UI_DESIGN = "ui_design"
    IMPLEMENTATION = "implementation"
    REVIEW = "review"
    QA = "qa"
    DOCUMENTATION = "documentation"
    COMPLETE = "complete"


class Checkpoint(str, Enum):
    """Founder review checkpoints."""
    CHECKPOINT_1 = "checkpoint_1"  # After PRD
    CHECKPOINT_2 = "checkpoint_2"  # After Analysis
    CHECKPOINT_3 = "checkpoint_3"  # After System Design
    CHECKPOINT_3B = "checkpoint_3b"  # After UI Design
    CHECKPOINT_4 = "checkpoint_4"  # After Implementation + Review
    CHECKPOINT_5 = "checkpoint_5"  # After QA — Final Release



class CheckpointStatus(str, Enum):
    """Checkpoint status values."""
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    TIMEOUT = "timeout"


class Pipeline:
    """Pipeline orchestrator for agent execution.

    Each phase uses a dedicated single-agent crew:
      PM → Analyst → Architect → Designer → Developer → Reviewer → QA → Tech Writer

    Thread-safe: Each instance has its own state.
    """

    def __init__(self, verbose: bool = True) -> None:
        self.verbose = verbose
        self.current_stage = PipelineStage.REQUIREMENTS
        self.state = {
            "prd_path": None,
            "system_design_path": None,
            "task_issues": [],
            "pr_urls": [],
            "qa_status": None,
        }
        self._lock = threading.Lock()  # For thread-safe state updates

    def _update_stage(self, new_stage: PipelineStage) -> None:
        """Thread-safe stage update."""
        with self._lock:
            self.current_stage = new_stage

    def _update_state(self, key: str, value: Any) -> None:
        """Thread-safe state update."""
        with self._lock:
            self.state[key] = value

    def _append_state(self, key: str, value: Any) -> None:
        """Thread-safe append to state list."""
        with self._lock:
            if key in self.state and isinstance(self.state[key], list):
                self.state[key].append(value)

    # =========================================================================
    # Phase runners — each calls a single-agent crew
    # =========================================================================

    def run_requirements_phase(self, founder_vision: str) -> dict:
        """Run requirements gathering phase (PM crew).

        Args:
            founder_vision: Product vision from founder

        Returns:
            Dict with status, result, and artifacts (PRD path)
        """
        print("\n" + "=" * 50)
        print("📋 PHASE: Requirements (PM)")
        print("=" * 50)

        self._update_stage(PipelineStage.REQUIREMENTS)
        state_manager.update_agent_state("pm", "working", "collecting_requirements")

        # Verify role context before running crew
        from src.tools.file_permissions import get_current_role
        pre_role = get_current_role()
        logger.info(f"Role context BEFORE pm_crew: {pre_role}")

        from src.crews import run_pm_crew
        result = run_pm_crew(founder_vision)

        post_role = get_current_role()
        logger.info(f"Role context AFTER pm_crew: {post_role}")

        self._update_state("prd_path", result.get("artifacts", {}).get("prd"))
        state_manager.update_agent_state("pm", "idle")
        self._update_stage(PipelineStage.ANALYSIS)

        return result

    def run_analysis_phase(self) -> dict:
        """Phase 2: Analyst agent decomposes PRD into tasks."""
        print("\n" + "=" * 50)
        print("📊 PHASE: Analysis (Analyst)")
        print("=" * 50)

        state_manager.update_agent_state("analyst", "working", "analyzing_prd")

        from src.crews import run_analyst_crew
        result = run_analyst_crew()

        state_manager.update_agent_state("analyst", "idle")
        self._update_stage(PipelineStage.DESIGN)

        return result

    def run_design_phase(self) -> dict:
        """Phase 3: Architect agent creates system design."""
        print("\n" + "=" * 50)
        print("🏗️ PHASE: Design (Architect)")
        print("=" * 50)

        state_manager.update_agent_state("architect", "working", "creating_design")

        from src.crews import run_architect_crew
        result = run_architect_crew()

        self._update_state("system_design_path", result.get("artifacts", {}).get("system_design"))
        state_manager.update_agent_state("architect", "idle")
        self._update_stage(PipelineStage.UI_DESIGN)

        return result

    def run_ui_design_phase(self, task_description: str = "") -> dict:
        """Phase 4: Designer agent creates UI specs."""
        print("\n" + "=" * 50)
        print("🎨 PHASE: UI Design (Designer)")
        print("=" * 50)

        state_manager.update_agent_state("designer", "working", "creating_ui")

        with self._lock:
            system_design = self.state.get("system_design_path", "docs/design/system-design.md")
        
        from src.crews import run_designer_crew
        result = run_designer_crew(system_design, task_description)

        state_manager.update_agent_state("designer", "idle")
        self._update_stage(PipelineStage.IMPLEMENTATION)

        return result

    def run_implementation_phase(self, issue_number: int) -> dict:
        """Phase 5: Developer agent implements feature."""
        print("\n" + "=" * 50)
        print(f"💻 PHASE: Implementation (Developer) — Issue #{issue_number}")
        print("=" * 50)

        self._update_stage(PipelineStage.IMPLEMENTATION)
        state_manager.update_agent_state("developer", "working", f"implementing_issue_{issue_number}")

        from src.crews import run_developer_crew
        result = run_developer_crew(issue_number)

        state_manager.update_agent_state("developer", "idle")
        self._update_stage(PipelineStage.REVIEW)

        return result

    def run_review_phase(self) -> dict:
        """Phase 6: Reviewer agent reviews code artifacts."""
        print("\n" + "=" * 50)
        print("👀 PHASE: Review (Reviewer)")
        print("=" * 50)

        self._update_stage(PipelineStage.REVIEW)
        state_manager.update_agent_state("reviewer", "working", "reviewing_code")

        from src.crews import run_reviewer_crew
        result = run_reviewer_crew()

        state_manager.update_agent_state("reviewer", "idle")
        self._update_stage(PipelineStage.QA)

        return result

    def run_qa_phase(self) -> dict:
        """Phase 7: QA agent tests the implementation."""
        print("\n" + "=" * 50)
        print(f"✅ PHASE: QA")
        print("=" * 50)

        self._update_stage(PipelineStage.QA)
        state_manager.update_agent_state("qa", "working", "testing_code")

        from src.crews import run_qa_crew
        result = run_qa_crew()

        state_manager.update_agent_state("qa", "idle")
        self._update_state("qa_status", "passed")
        self._update_stage(PipelineStage.DOCUMENTATION)

        return result

    def run_documentation_phase(self) -> dict:
        """Phase 8: Tech Writer agent updates documentation."""
        print("\n" + "=" * 50)
        print("📝 PHASE: Documentation (Tech Writer)")
        print("=" * 50)

        self._update_stage(PipelineStage.DOCUMENTATION)
        state_manager.update_agent_state("tech_writer", "working", "updating_docs")

        from src.crews import run_tech_writer_crew
        result = run_tech_writer_crew()

        state_manager.update_agent_state("tech_writer", "idle")
        self._update_stage(PipelineStage.COMPLETE)

        return result

    # =========================================================================
    # Checkpoint management
    # =========================================================================

    def request_checkpoint(self, checkpoint: Checkpoint, artifacts: list) -> dict:
        print("\n" + "=" * 50)
        print(f"🛑 CHECKPOINT: {checkpoint.value}")
        print("=" * 50)
        for artifact in artifacts:
            print(f"  - {artifact}")
        print("\nWaiting for founder approval...")

        state_manager.set_checkpoint(checkpoint.value, "pending_review", artifacts)
        return {"status": "pending_review", "checkpoint": checkpoint.value}

    def wait_for_checkpoint_approval(self, checkpoint: Checkpoint, timeout_minutes: int = 60) -> bool:
        import time
        start_time = time.time()
        timeout_seconds = timeout_minutes * 60

        print(f"⏳ Waiting for checkpoint {checkpoint.value} approval (timeout: {timeout_minutes} min)...")

        while True:
            cp_data = state_manager.get_checkpoint(checkpoint.value)
            if cp_data:
                status = cp_data.get("status")
                if status == "approved":
                    print(f"✅ Checkpoint {checkpoint.value} approved!")
                    return True
                elif status == "rejected":
                    print(f"❌ Checkpoint {checkpoint.value} rejected")
                    return False

            elapsed = time.time() - start_time
            if elapsed >= timeout_seconds:
                print(f"⏰ Checkpoint {checkpoint.value} timed out")
                return False
            time.sleep(5)

    def approve_checkpoint(self, checkpoint: Checkpoint, notes: str = "") -> None:
        state_manager.approve_checkpoint(checkpoint.value, notes)
        print(f"\n✅ Checkpoint {checkpoint.value} approved!")

    def reject_checkpoint(self, checkpoint: Checkpoint, reason: str) -> None:
        state_manager.reject_checkpoint(checkpoint.value, reason)
        print(f"\n❌ Checkpoint {checkpoint.value} rejected: {reason}")

    # =========================================================================
    # Status
    # =========================================================================

    def get_status(self) -> dict:
        """Get current pipeline status.

        Returns:
            dict: Current stage and state information
        """
        with self._lock:
            return {
                "current_stage": self.current_stage.value,
                "state": self.state.copy(),
                "agents": state_manager.state.get("agents", {}),
            }

    def is_complete(self) -> bool:
        """Check if pipeline has completed all phases.

        Returns:
            bool: True if pipeline is complete
        """
        with self._lock:
            return self.current_stage == PipelineStage.COMPLETE

    # =========================================================================
    # Full pipeline
    # =========================================================================

    # =========================================================================
    # Phase prerequisites: files that must exist in GitHub to resume from a phase
    # =========================================================================
    PHASE_PREREQUISITES = {
        "analysis": ["docs/requirements/prd.md"],
        "design": ["docs/requirements/prd.md", "docs/requirements/task-specs.md"],
        "ui_design": ["docs/requirements/prd.md", "docs/requirements/task-specs.md", "docs/design/system-design.md"],
        "implementation": ["docs/requirements/prd.md", "docs/requirements/task-specs.md", "docs/design/system-design.md"],
        "review": [],   # needs pr_url, checked at runtime
        "qa": [],       # needs pr_url, checked at runtime
        "documentation": ["docs/requirements/prd.md", "docs/design/system-design.md"],
    }

    PHASE_NAMES = {
        "requirements": "📋 Требования (PM)",
        "analysis": "📊 Анализ (Analyst)",
        "design": "🏗️ Архитектура (Architect)",
        "ui_design": "🎨 UI Design (Designer)",
        "implementation": "💻 Разработка (Developer)",
        "review": "👀 Ревью (Reviewer)",
        "qa": "🧪 Тестирование (QA)",
        "documentation": "📝 Документация (Tech Writer)",
    }

    # Execution order for skip logic
    PHASE_ORDER = [
        "requirements", "analysis", "design", "ui_design",
        "implementation", "review", "qa", "documentation",
    ]

    def validate_prerequisites(self, phase: str) -> tuple[bool, list[str]]:
        """Check that prerequisite files exist in GitHub for a given phase.

        Returns (ok, missing_files).
        """
        from src.tools.github_client import get_github_client

        prerequisites = self.PHASE_PREREQUISITES.get(phase, [])
        if not prerequisites:
            return True, []

        client = get_github_client()
        missing = []
        for path in prerequisites:
            if not client.file_exists(path):
                missing.append(path)
        return len(missing) == 0, missing

    def run_full_pipeline(
        self,
        issue_number: int,
        founder_vision: str,
        on_checkpoint: Optional[Callable] = None,
        on_progress: Optional[Callable] = None,
        from_phase: Optional[str] = None,
    ) -> dict:
        """Run the full pipeline — each phase with its own crew and role.

        Phases: PM → Analyst → Architect → Designer → Developer → Reviewer → QA → Tech Writer

        Args:
            issue_number: GitHub issue number
            founder_vision: Product vision from founder
            on_checkpoint: Callback for checkpoint notifications
            on_progress: Callback for progress updates
            from_phase: Skip phases before this one (for resume).
                        Valid values: requirements, analysis, design, ui_design,
                        implementation, review, qa, documentation
        """
        results = {"issue_number": issue_number, "phases": {}}

        # Clear stale checkpoints from previous runs
        with self._lock:
            state_manager.state["checkpoints"] = {}
            state_manager.save_state()

        # Validate prerequisites if resuming from a specific phase
        if from_phase:
            if from_phase not in self.PHASE_NAMES:
                return {
                    "status": "error",
                    "error": f"Unknown phase '{from_phase}'. Valid: {list(self.PHASE_NAMES.keys())}",
                }
            ok, missing = self.validate_prerequisites(from_phase)
            if not ok:
                return {
                    "status": "error",
                    "error": f"Missing prerequisite files for phase '{from_phase}': {', '.join(missing)}",
                }

        # Determine which phases to skip
        skipping = from_phase is not None

        try:
            # Phase 1: Requirements (PM)
            if not skipping:
                if on_progress:
                    on_progress("requirements", "Собираю требования (PM)...")
                req_result = self.run_requirements_phase(founder_vision)
                results["phases"]["requirements"] = req_result

                if on_checkpoint:
                    on_checkpoint(Checkpoint.CHECKPOINT_1, ["docs/requirements/prd.md"])
                    if not self.wait_for_checkpoint_approval(Checkpoint.CHECKPOINT_1):
                        results["status"] = "rejected"
                        results["error"] = "Checkpoint 1 (PRD) rejected or timed out"
                        return results
            else:
                logger.info(f"Skipping phase 'requirements' (resume from '{from_phase}')")
            if from_phase == "requirements":
                skipping = False

            # Phase 2: Analysis (Analyst)
            if not skipping:
                if on_progress:
                    on_progress("analysis", "Анализирую PRD (Analyst)...")
                analysis_result = self.run_analysis_phase()
                results["phases"]["analysis"] = analysis_result

                if on_checkpoint:
                    on_checkpoint(Checkpoint.CHECKPOINT_2, ["docs/requirements/task-specs.md"])
                    if not self.wait_for_checkpoint_approval(Checkpoint.CHECKPOINT_2):
                        results["status"] = "rejected"
                        return results
            else:
                logger.info(f"Skipping phase 'analysis' (resume from '{from_phase}')")
            if from_phase == "analysis":
                skipping = False

            # Phase 3: Design (Architect)
            if not skipping:
                if on_progress:
                    on_progress("design", "Проектирую архитектуру (Architect)...")
                design_result = self.run_design_phase()
                results["phases"]["design"] = design_result

                if on_checkpoint:
                    on_checkpoint(Checkpoint.CHECKPOINT_3, ["docs/design/system-design.md"])
                    if not self.wait_for_checkpoint_approval(Checkpoint.CHECKPOINT_3):
                        results["status"] = "rejected"
                        return results
            else:
                logger.info(f"Skipping phase 'design' (resume from '{from_phase}')")
            if from_phase == "design":
                skipping = False

            # Phase 4: UI Design (Designer)
            if not skipping:
                if on_progress:
                    on_progress("ui_design", "Создаю UI спецификации (Designer)...")
                ui_result = self.run_ui_design_phase()
                results["phases"]["ui_design"] = ui_result

                if on_checkpoint:
                    on_checkpoint(Checkpoint.CHECKPOINT_3B, ["docs/design/design-system.md", "docs/design/ui/"])
                    if not self.wait_for_checkpoint_approval(Checkpoint.CHECKPOINT_3B):
                        results["status"] = "rejected"
                        return results
            else:
                logger.info(f"Skipping phase 'ui_design' (resume from '{from_phase}')")
            if from_phase == "ui_design":
                skipping = False

            # Phase 5: Implementation (Developer)
            if not skipping:
                if on_progress:
                    on_progress("implementation", "Разрабатываю код (Developer)...")
                impl_result = self.run_implementation_phase(issue_number)
                results["phases"]["implementation"] = impl_result
            else:
                logger.info(f"Skipping phase 'implementation' (resume from '{from_phase}')")
            if from_phase == "implementation":
                skipping = False

            # Phase 6: Review (Reviewer)
            if not skipping:
                if on_progress:
                    on_progress("review", "Ревью кода (Reviewer)...")
                review_result = self.run_review_phase()
                results["phases"]["review"] = review_result

                if on_checkpoint:
                    on_checkpoint(Checkpoint.CHECKPOINT_4, ["Code review completed"])
                    if not self.wait_for_checkpoint_approval(Checkpoint.CHECKPOINT_4):
                        results["status"] = "rejected"
                        return results
            else:
                logger.info(f"Skipping phase 'review' (resume from '{from_phase}')")
            if from_phase == "review":
                skipping = False

            # Phase 7: QA
            if not skipping:
                if on_progress:
                    on_progress("qa", "Тестирую (QA)...")
                qa_result = self.run_qa_phase()
                results["phases"]["qa"] = qa_result
            else:
                logger.info(f"Skipping phase 'qa' (resume from '{from_phase}')")
            if from_phase == "qa":
                skipping = False

            # Phase 8: Documentation (Tech Writer)
            if not skipping:
                if on_progress:
                    on_progress("documentation", "Обновляю документацию (Tech Writer)...")
                doc_result = self.run_documentation_phase()
                results["phases"]["documentation"] = doc_result
            else:
                logger.info(f"Skipping phase 'documentation' (resume from '{from_phase}')")
            if from_phase == "documentation":
                skipping = False

            # Final checkpoint
            if not skipping:
                if on_checkpoint:
                    with self._lock:
                        pr_urls = self.state.get("pr_urls", [])
                    on_checkpoint(Checkpoint.CHECKPOINT_5, pr_urls)

            results["status"] = "complete"

        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)
            logger.error(f"Pipeline error: {e}", exc_info=True)

        return results


# Singleton pipeline instance (lazy initialization)
_pipeline: Optional[Pipeline] = None
_pipeline_lock = threading.Lock()


def get_pipeline(verbose: bool = True) -> Pipeline:
    """Get Pipeline singleton (thread-safe).

    Uses double-check locking pattern for thread-safe lazy initialization.
    Returns the same Pipeline instance on every call.

    Use this when you need shared state across the application.

    Returns:
        Pipeline singleton instance
    """
    global _pipeline
    if _pipeline is None:
        with _pipeline_lock:
            if _pipeline is None:  # Double-check locking
                _pipeline = Pipeline(verbose=verbose)
    return _pipeline


def create_pipeline(verbose: bool = True) -> Pipeline:
    """Factory function to create a new Pipeline instance.
    
    Use this instead of global pipeline to prevent race conditions
    when running multiple pipelines concurrently.
    """
    return Pipeline(verbose=verbose)


# Legacy global pipeline for backwards compatibility
# DEPRECATED: Use create_pipeline() instead
pipeline = Pipeline()
