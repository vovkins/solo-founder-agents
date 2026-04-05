"""Event handlers for pipeline events.

Architecture improvement C: Event-driven checkpoint handling.
"""

import logging
import threading
from typing import Dict, Any, Optional
from .bus import EventBus, Event

logger = logging.getLogger(__name__)


class CheckpointHandler:
    """Handles checkpoint events with approval/rejection logic.
    
    Event types:
    - checkpoint.created: New checkpoint created
    - checkpoint.approved: Checkpoint approved
    - checkpoint.rejected: Checkpoint rejected
    - checkpoint.timeout: Checkpoint timed out
    """
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self._lock = threading.Lock()
        self._checkpoints: Dict[str, Dict[str, Any]] = {}
        
        # Subscribe to checkpoint events
        self.event_bus.subscribe("checkpoint.created", self._on_created)
        self.event_bus.subscribe("checkpoint.approved", self._on_approved)
        self.event_bus.subscribe("checkpoint.rejected", self._on_rejected)
    
    def _on_created(self, event: Event) -> None:
        """Handle checkpoint created event."""
        with self._lock:
            checkpoint_id = event.data.get("checkpoint_id")
            self._checkpoints[checkpoint_id] = {
                "status": "pending",
                "artifacts": event.data.get("artifacts", []),
                "created_at": event.timestamp
            }
            logger.info(f"Checkpoint created: {checkpoint_id}")
    
    def _on_approved(self, event: Event) -> None:
        """Handle checkpoint approved event."""
        with self._lock:
            checkpoint_id = event.data.get("checkpoint_id")
            if checkpoint_id in self._checkpoints:
                self._checkpoints[checkpoint_id]["status"] = "approved"
                self._checkpoints[checkpoint_id]["approved_at"] = event.timestamp
                logger.info(f"Checkpoint approved: {checkpoint_id}")
    
    def _on_rejected(self, event: Event) -> None:
        """Handle checkpoint rejected event."""
        with self._lock:
            checkpoint_id = event.data.get("checkpoint_id")
            if checkpoint_id in self._checkpoints:
                self._checkpoints[checkpoint_id]["status"] = "rejected"
                self._checkpoints[checkpoint_id]["rejected_at"] = event.timestamp
                logger.info(f"Checkpoint rejected: {checkpoint_id}")
    
    def create_checkpoint(
        self,
        checkpoint_id: str,
        artifacts: list
    ) -> None:
        """Create a new checkpoint.
        
        Args:
            checkpoint_id: Checkpoint identifier
            artifacts: List of artifact paths
        """
        self.event_bus.publish("checkpoint.created", {
            "checkpoint_id": checkpoint_id,
            "artifacts": artifacts
        })
    
    def approve_checkpoint(
        self,
        checkpoint_id: str,
        notes: Optional[str] = None
    ) -> None:
        """Approve a checkpoint.
        
        Args:
            checkpoint_id: Checkpoint identifier
            notes: Optional approval notes
        """
        self.event_bus.publish("checkpoint.approved", {
            "checkpoint_id": checkpoint_id,
            "notes": notes
        })
    
    def reject_checkpoint(
        self,
        checkpoint_id: str,
        reason: str
    ) -> None:
        """Reject a checkpoint.
        
        Args:
            checkpoint_id: Checkpoint identifier
            reason: Rejection reason
        """
        self.event_bus.publish("checkpoint.rejected", {
            "checkpoint_id": checkpoint_id,
            "reason": reason
        })
    
    def get_checkpoint_status(self, checkpoint_id: str) -> Optional[str]:
        """Get checkpoint status.
        
        Args:
            checkpoint_id: Checkpoint identifier
        
        Returns:
            Status string or None
        """
        with self._lock:
            return self._checkpoints.get(checkpoint_id, {}).get("status")
    
    def wait_for_approval(
        self,
        checkpoint_id: str,
        timeout_minutes: int = 60
    ) -> bool:
        """Wait for checkpoint approval (polling-based for now).
        
        Args:
            checkpoint_id: Checkpoint identifier
            timeout_minutes: Timeout in minutes
        
        Returns:
            True if approved, False if rejected or timeout
        """
        import time
        
        start_time = time.time()
        timeout_seconds = timeout_minutes * 60
        
        while True:
            status = self.get_checkpoint_status(checkpoint_id)
            
            if status == "approved":
                return True
            elif status == "rejected":
                return False
            
            elapsed = time.time() - start_time
            if elapsed >= timeout_seconds:
                self.event_bus.publish("checkpoint.timeout", {
                    "checkpoint_id": checkpoint_id
                })
                return False
            
            time.sleep(5)


# Global checkpoint handler instance
from .bus import event_bus
checkpoint_handler = CheckpointHandler(event_bus)
