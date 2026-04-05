"""Agent cache with TTL and LRU eviction.

Architecture improvement A: Separates caching concerns with proper TTL/eviction.
"""

import logging
import threading
import time
from collections import OrderedDict
from typing import Any, Optional, Callable

logger = logging.getLogger(__name__)


class AgentCache:
    """Thread-safe agent cache with TTL and LRU eviction.
    
    Args:
        max_size: Maximum number of agents to cache (default: 20)
        ttl_seconds: Time-to-live in seconds (default: 1800 = 30 minutes)
    """
    
    def __init__(self, max_size: int = 20, ttl_seconds: int = 1800):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._lock = threading.Lock()
        self._cache: OrderedDict = OrderedDict()  # agent_name -> (agent, timestamp)
    
    def get(self, agent_name: str) -> Optional[Any]:
        """Get agent from cache if exists and not expired.
        
        Args:
            agent_name: Name of the agent (e.g., "pm", "analyst")
        
        Returns:
            Agent instance or None if not found/expired
        """
        with self._lock:
            if agent_name not in self._cache:
                return None
            
            agent, timestamp = self._cache[agent_name]
            
            # Check TTL
            if self.ttl_seconds > 0:
                age = time.time() - timestamp
                if age > self.ttl_seconds:
                    logger.info(f"Agent cache entry expired: {agent_name} (age: {age:.0f}s)")
                    del self._cache[agent_name]
                    return None
            
            # Move to end (most recently used)
            self._cache.move_to_end(agent_name)
            return agent
    
    def set(self, agent_name: str, agent: Any) -> None:
        """Add agent to cache with timestamp.
        
        Args:
            agent_name: Name of the agent
            agent: Agent instance to cache
        """
        with self._lock:
            # Remove if exists (to update timestamp)
            if agent_name in self._cache:
                del self._cache[agent_name]
            
            # Add to cache
            self._cache[agent_name] = (agent, time.time())
            
            # Evict oldest if over max size
            while len(self._cache) > self.max_size:
                oldest_key = next(iter(self._cache))
                logger.info(f"Agent cache evicting: {oldest_key}")
                del self._cache[oldest_key]
    
    def get_or_create(
        self,
        agent_name: str,
        factory_func: Callable[[], Any]
    ) -> Any:
        """Get agent from cache or create using factory function.
        
        Args:
            agent_name: Name of the agent
            factory_func: Function to create agent if not cached
        
        Returns:
            Agent instance (from cache or newly created)
        """
        agent = self.get(agent_name)
        if agent is None:
            logger.debug(f"Creating new agent instance: {agent_name}")
            agent = factory_func()
            self.set(agent_name, agent)
        else:
            logger.debug(f"Using cached agent instance: {agent_name}")
        return agent
    
    def clear(self) -> None:
        """Clear all cached agents."""
        with self._lock:
            self._cache.clear()
            logger.info("Agent cache cleared")
    
    def size(self) -> int:
        """Get current cache size."""
        with self._lock:
            return len(self._cache)
    
    def stats(self) -> dict:
        """Get cache statistics."""
        with self._lock:
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "ttl_seconds": self.ttl_seconds,
                "agents": list(self._cache.keys())
            }


# Global agent cache instance
agent_cache = AgentCache(max_size=20, ttl_seconds=1800)
