"""State management for tracking progress and context."""

import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


# State file location
DATA_DIR = Path("data")
STATE_DIR = DATA_DIR / "state"
STATE_FILE = STATE_DIR / "state.json"


def ensure_state_dir() -> None:
    """Ensure state directory exists."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)


class StateManager:
    """Manager for application state."""

    def __init__(self):
        """Initialize state manager and load existing state."""
        self._lock = threading.Lock()
        self.state = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        """Load state from file (thread-safe).

        Returns:
            State dictionary
        """
        with self._lock:
            ensure_state_dir()
            if STATE_FILE.exists():
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)

        # Default state structure
        return {
            "tasks": {},  # task_id -> {status, updated_at, ...}
            "checkpoints": {},  # checkpoint_id -> {status, artifacts, ...}
            "agents": {},  # agent_name -> {last_run, status, ...}
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            },
        }

    def save_state(self) -> None:
        """Save state to file (thread-safe)."""
        with self._lock:
            ensure_state_dir()
            self.state["metadata"]["updated_at"] = datetime.now().isoformat()
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.state, f, indent=2)

    # ===========================================
    # Task State
    # ===========================================

    def set_task_status(
        self,
        task_id: str,
        status: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Set status for a task."""
        with self._lock:
            self.state["tasks"][task_id] = {
                "status": status,
                "updated_at": datetime.now().isoformat(),
                **(details or {}),
            }
            self.save_state()

    def get_task_status(self, task_id: str) -> Optional[str]:
        """Get status for a task.

        Args:
            task_id: Task identifier

        Returns:
            Status string or None if not found
        """
        return self.state["tasks"].get(task_id, {}).get("status")

    def get_task_details(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get full details for a task.

        Args:
            task_id: Task identifier

        Returns:
            Task details dictionary or None
        """
        return self.state["tasks"].get(task_id)

    def list_tasks_by_status(self, status: str) -> List[str]:
        """List all tasks with a specific status.

        Args:
            status: Status to filter by

        Returns:
            List of task IDs
        """
        return [
            task_id
            for task_id, task_data in self.state["tasks"].items()
            if task_data.get("status") == status
        ]

    # ===========================================
    # Checkpoint State
    # ===========================================

    def set_checkpoint(
        self,
        checkpoint_id: str,
        status: str,
        artifacts: Optional[List[str]] = None,
        notes: Optional[str] = None,
    ) -> None:
        """Set checkpoint status.

        Args:
            checkpoint_id: Checkpoint identifier
            status: Status (pending_review, approved, rejected)
            artifacts: List of artifact paths to review
            notes: Optional notes
        """
        self.state["checkpoints"][checkpoint_id] = {
            "status": status,
            "artifacts": artifacts or [],
            "notes": notes,
            "updated_at": datetime.now().isoformat(),
        }
        self.save_state()

    def get_checkpoint(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """Get checkpoint details.

        Args:
            checkpoint_id: Checkpoint identifier

        Returns:
            Checkpoint details or None
        """
        return self.state["checkpoints"].get(checkpoint_id)

    def approve_checkpoint(self, checkpoint_id: str, notes: Optional[str] = None) -> None:
        """Approve a checkpoint.

        Args:
            checkpoint_id: Checkpoint identifier
            notes: Optional approval notes
        """
        self.set_checkpoint(checkpoint_id, "approved", notes=notes)

    def reject_checkpoint(self, checkpoint_id: str, notes: str) -> None:
        """Reject a checkpoint.

        Args:
            checkpoint_id: Checkpoint identifier
            notes: Rejection reason
        """
        self.set_checkpoint(checkpoint_id, "rejected", notes=notes)

    # ===========================================
    # Agent State
    # ===========================================

    def update_agent_state(
        self,
        agent_name: str,
        status: str,
        current_task: Optional[str] = None,
    ) -> None:
        """Update agent state.

        Args:
            agent_name: Agent name (e.g., 'pm', 'developer')
            status: Status (idle, working, error)
            current_task: Current task ID if working
        """
        self.state["agents"][agent_name] = {
            "status": status,
            "current_task": current_task,
            "updated_at": datetime.now().isoformat(),
        }
        self.save_state()

    def get_agent_state(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get agent state.

        Args:
            agent_name: Agent name

        Returns:
            Agent state dictionary or None
        """
        return self.state["agents"].get(agent_name)

    # ===========================================
    # General State
    # ===========================================

    def get_full_state(self) -> Dict[str, Any]:
        """Get the complete state.

        Returns:
            Full state dictionary
        """
        return self.state.copy()

    def clear_state(self) -> None:
        """Clear all state."""
        self.state = {
            "tasks": {},
            "checkpoints": {},
            "agents": {},
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            },
        }
        self.save_state()


# Global state manager instance
state_manager = StateManager()
