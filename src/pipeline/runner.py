"""Pipeline runner for orchestrating multi-agent execution.

Architecture improvement B: Separates pipeline orchestration logic.
"""

import logging
from typing import Optional, Callable, Dict, Any

logger = logging.getLogger(__name__)


class PipelineRunner:
    """Orchestrates pipeline execution with clean separation of concerns.
    
    Responsibilities:
    - Run individual phases
    - Handle checkpoints
    - Manage state transitions
    - Provide error recovery
    """
    
    def __init__(self, pipeline):
        """Initialize runner with pipeline instance.
        
        Args:
            pipeline: Pipeline instance to orchestrate
        """
        self.pipeline = pipeline
        self.results = {}
    
    def run_phase(
        self,
        phase_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Run a single pipeline phase.
        
        Args:
            phase_name: Name of phase (requirements, analysis, etc.)
            **kwargs: Phase-specific arguments
        
        Returns:
            Phase result dictionary
        """
        logger.info(f"Running phase: {phase_name}")
        
        phase_map = {
            "requirements": self.pipeline.run_requirements_phase,
            "analysis": self.pipeline.run_analysis_phase,
            "design": self.pipeline.run_design_phase,
            "ui_design": self.pipeline.run_ui_design_phase,
            "implementation": self.pipeline.run_implementation_phase,
            "review": self.pipeline.run_review_phase,
            "qa": self.pipeline.run_qa_phase,
            "documentation": self.pipeline.run_documentation_phase,
        }
        
        if phase_name not in phase_map:
            raise ValueError(f"Unknown phase: {phase_name}")
        
        try:
            result = phase_map[phase_name](**kwargs)
            self.results[phase_name] = result
            return result
        except Exception as e:
            logger.error(f"Phase {phase_name} failed: {e}", exc_info=True)
            raise
    
    def run_all(
        self,
        issue_number: int,
        founder_vision: str,
        on_checkpoint: Optional[Callable] = None,
        on_progress: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """Run complete pipeline with all phases.
        
        Args:
            issue_number: GitHub issue number
            founder_vision: Founder's product vision
            on_checkpoint: Callback for checkpoint events
            on_progress: Callback for progress updates
        
        Returns:
            Complete pipeline results
        """
        results = {"issue_number": issue_number, "phases": {}}
        
        try:
            # Phase 1: Requirements
            if on_progress:
                on_progress("requirements", "Собираю требования (PM)...")
            req_result = self.run_phase("requirements", founder_vision=founder_vision)
            results["phases"]["requirements"] = req_result
            
            # Checkpoint 1
            if on_checkpoint:
                self._handle_checkpoint(
                    self.pipeline.Checkpoint.CHECKPOINT_1,
                    ["docs/requirements/prd.md"],
                    on_checkpoint
                )
            
            # Phase 2: Analysis
            if on_progress:
                on_progress("analysis", "Анализирую PRD (Analyst)...")
            analysis_result = self.run_phase("analysis")
            results["phases"]["analysis"] = analysis_result
            
            # Checkpoint 2
            if on_checkpoint:
                self._handle_checkpoint(
                    self.pipeline.Checkpoint.CHECKPOINT_2,
                    ["docs/requirements/task-specs.md"],
                    on_checkpoint
                )
            
            # Phase 3: Design
            if on_progress:
                on_progress("design", "Проектирую архитектуру (Architect)...")
            design_result = self.run_phase("design")
            results["phases"]["design"] = design_result
            
            # Checkpoint 3
            if on_checkpoint:
                self._handle_checkpoint(
                    self.pipeline.Checkpoint.CHECKPOINT_3,
                    ["docs/design/system-design.md"],
                    on_checkpoint
                )
            
            # Phase 4: UI Design
            if on_progress:
                on_progress("ui_design", "Создаю UI спецификации (Designer)...")
            ui_result = self.run_phase("ui_design")
            results["phases"]["ui_design"] = ui_result
            
            # Phase 5: Implementation
            if on_progress:
                on_progress("implementation", "Разрабатываю код (Developer)...")
            impl_result = self.run_phase("implementation", issue_number=issue_number)
            results["phases"]["implementation"] = impl_result
            
            pr_url = impl_result.get("pr_url")
            if pr_url:
                # Phase 6: Review
                if on_progress:
                    on_progress("review", "Ревью кода (Reviewer)...")
                review_result = self.run_phase("review", pr_url=pr_url)
                results["phases"]["review"] = review_result
                
                # Checkpoint 4
                if on_checkpoint:
                    self._handle_checkpoint(
                        self.pipeline.Checkpoint.CHECKPOINT_4,
                        [pr_url],
                        on_checkpoint
                    )
                
                # Phase 7: QA
                if on_progress:
                    on_progress("qa", "Тестирую (QA)...")
                qa_result = self.run_phase("qa", pr_url=pr_url)
                results["phases"]["qa"] = qa_result
            
            # Phase 8: Documentation
            if on_progress:
                on_progress("documentation", "Обновляю документацию (Tech Writer)...")
            doc_result = self.run_phase("documentation")
            results["phases"]["documentation"] = doc_result
            
            # Checkpoint 5 (Final)
            if on_checkpoint:
                with self.pipeline._lock:
                    pr_urls = self.pipeline.state.get("pr_urls", [])
                self._handle_checkpoint(
                    self.pipeline.Checkpoint.CHECKPOINT_5,
                    pr_urls,
                    on_checkpoint
                )
            
            results["status"] = "complete"
            
        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)
            logger.error(f"Pipeline failed: {e}", exc_info=True)
        
        return results
    
    def _handle_checkpoint(
        self,
        checkpoint,
        artifacts: list,
        on_checkpoint: Callable
    ) -> bool:
        """Handle checkpoint approval process.
        
        Args:
            checkpoint: Checkpoint enum value
            artifacts: List of artifact paths
            on_checkpoint: Callback function
        
        Returns:
            True if approved, False otherwise
        """
        on_checkpoint(checkpoint, artifacts)
        
        # Wait for approval
        approved = self.pipeline.wait_for_checkpoint_approval(checkpoint)
        
        if not approved:
            logger.warning(f"Checkpoint {checkpoint.value} not approved")
            raise RuntimeError(f"Checkpoint {checkpoint.value} rejected or timed out")
        
        return True
    
    def get_results(self) -> Dict[str, Any]:
        """Get all phase results.
        
        Returns:
            Dictionary of phase results
        """
        return self.results.copy()
    
    def clear_results(self) -> None:
        """Clear all stored results."""
        self.results.clear()
