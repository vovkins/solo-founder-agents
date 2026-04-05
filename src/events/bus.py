"""Event bus for pub/sub messaging.

Architecture improvement C: Event-driven architecture.
"""

import logging
import asyncio
import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from queue import Queue

logger = logging.getLogger(__name__)


@dataclass
class Event:
    """Event data structure."""
    
    event_type: str
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_type": self.event_type,
            "data": self.data,
            "timestamp": self.timestamp.isoformat()
        }


class EventBus:
    """Thread-safe event bus for pub/sub messaging.
    
    Supports:
    - Subscribe to events
    - Publish events
    - Async event handling
    - Event history
    """
    
    def __init__(self):
        self._lock = threading.Lock()
        self._subscribers: Dict[str, List[Callable]] = {}
        self._event_queue: Queue = Queue()
        self._history: List[Event] = []
        self._max_history = 100
    
    def subscribe(
        self,
        event_type: str,
        callback: Callable[[Event], None]
    ) -> None:
        """Subscribe to events of a specific type.
        
        Args:
            event_type: Type of event to subscribe to
            callback: Function to call when event is published
        """
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(callback)
            logger.debug(f"Subscribed to event: {event_type}")
    
    def unsubscribe(
        self,
        event_type: str,
        callback: Callable[[Event], None]
    ) -> None:
        """Unsubscribe from events.
        
        Args:
            event_type: Type of event
            callback: Callback to remove
        """
        with self._lock:
            if event_type in self._subscribers:
                try:
                    self._subscribers[event_type].remove(callback)
                    logger.debug(f"Unsubscribed from event: {event_type}")
                except ValueError:
                    pass
    
    def publish(
        self,
        event_type: str,
        data: Dict[str, Any]
    ) -> Event:
        """Publish an event to all subscribers.
        
        Args:
            event_type: Type of event
            data: Event data
        
        Returns:
            Published event
        """
        event = Event(event_type=event_type, data=data)
        
        # Add to history
        with self._lock:
            self._history.append(event)
            if len(self._history) > self._max_history:
                self._history.pop(0)
        
        # Notify subscribers
        with self._lock:
            subscribers = self._subscribers.get(event_type, [])
        
        for callback in subscribers:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Error in event callback: {e}", exc_info=True)
        
        logger.debug(f"Published event: {event_type} to {len(subscribers)} subscribers")
        return event
    
    def publish_async(
        self,
        event_type: str,
        data: Dict[str, Any]
    ) -> Event:
        """Publish event asynchronously.
        
        Args:
            event_type: Type of event
            data: Event data
        
        Returns:
            Published event
        """
        event = self.publish(event_type, data)
        self._event_queue.put(event)
        return event
    
    def get_history(
        self,
        event_type: Optional[str] = None
    ) -> List[Event]:
        """Get event history.
        
        Args:
            event_type: Filter by event type (optional)
        
        Returns:
            List of events
        """
        with self._lock:
            if event_type:
                return [e for e in self._history if e.event_type == event_type]
            return self._history.copy()
    
    def clear_history(self) -> None:
        """Clear event history."""
        with self._lock:
            self._history.clear()
    
    def get_subscribers(self, event_type: str) -> List[Callable]:
        """Get list of subscribers for an event type.
        
        Args:
            event_type: Event type
        
        Returns:
            List of callbacks
        """
        with self._lock:
            return self._subscribers.get(event_type, []).copy()


# Global event bus instance
event_bus = EventBus()
