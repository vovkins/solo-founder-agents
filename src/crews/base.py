"""CrewAI base configuration and utilities.

FIX: Added TTL and LRU eviction to LLM cache to prevent memory leaks.
"""

import logging
import threading
import time
from collections import OrderedDict
from typing import Optional

from crewai import LLM
from config.settings import settings

logger = logging.getLogger(__name__)


def create_llm(model: str) -> LLM:
    """Create an LLM instance configured for OpenRouter."""
    return LLM(
        model=f"openrouter/{model}",
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
    )


class LRUCache:
    """Thread-safe LRU cache with TTL support.
    
    Args:
        max_size: Maximum number of items in cache
        ttl_seconds: Time-to-live in seconds (0 = no TTL)
    """
    
    def __init__(self, max_size: int = 10, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._lock = threading.Lock()
        self._cache: OrderedDict = OrderedDict()
        self._cleanup_thread = None
        self._running = True
        self._start_cleanup_thread()  # model_name -> (LLM, timestamp)
    

    def _start_cleanup_thread(self) -> None:
        """Start background cleanup thread."""
        def cleanup_loop():
            while self._running:
                time.sleep(300)  # Every 5 minutes
                self._cleanup_expired()
        
        self._cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        self._cleanup_thread.start()
        logger.info("LRU cache cleanup thread started (TTL: %ds, max_size: %d)", 
                   self.ttl_seconds, self.max_size)
    
    def _cleanup_expired(self) -> None:
        """Remove expired entries from cache."""
        with self._lock:
            current_time = time.time()
            expired = [
                k for k, (_, ts) in self._cache.items()
                if current_time - ts > self.ttl_seconds
            ]
            for k in expired:
                del self._cache[k]
                logger.info("Cleaned up expired cache entry: %s (age: %.0fs)", 
                           k, current_time - self._cache.get(k, (None, 0))[1] if k in self._cache else 0)
            
            if expired:
                logger.info("Cleaned up %d expired entries, cache size: %d", 
                           len(expired), len(self._cache))

    def stop_cleanup(self) -> None:
        """Stop cleanup thread (for testing/graceful shutdown)."""
        self._running = False
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=1)

    def get(self, model_name: str) -> Optional[LLM]:
        """Get LLM from cache if exists and not expired."""
        with self._lock:
            if model_name not in self._cache:
                return None
            
            llm, timestamp = self._cache[model_name]
            
            # Check TTL
            if self.ttl_seconds > 0:
                age = time.time() - timestamp
                if age > self.ttl_seconds:
                    logger.info(f"LLM cache entry expired: {model_name} (age: {age:.0f}s)")
                    del self._cache[model_name]
                    return None
            
            # Move to end (most recently used)
            self._cache.move_to_end(model_name)
            return llm
    
    def set(self, model_name: str, llm: LLM) -> None:
        """Add LLM to cache with timestamp."""
        with self._lock:
            # Remove if exists (to update timestamp)
            if model_name in self._cache:
                del self._cache[model_name]
            
            # Add to cache
            self._cache[model_name] = (llm, time.time())
            
            # Evict oldest if over max size
            while len(self._cache) > self.max_size:
                oldest_key = next(iter(self._cache))
                logger.info(f"LLM cache evicting: {oldest_key}")
                del self._cache[oldest_key]
    
    def clear(self) -> None:
        """Clear all cached entries."""
        with self._lock:
            self._cache.clear()
            logger.info("LLM cache cleared")
    
    def size(self) -> int:
        """Get current cache size."""
        with self._lock:
            return len(self._cache)


# Global LLM cache with TTL (1 hour) and max 10 models
_llm_cache = LRUCache(max_size=10, ttl_seconds=3600)


def _get_or_create_llm(model_name: str) -> LLM:
    """Get cached LLM or create a new one.
    
    Cache has TTL of 1 hour and max size of 10 models.
    Eviction policy: LRU (least recently used).
    """
    llm = _llm_cache.get(model_name)
    if llm is None:
        logger.debug(f"Creating new LLM instance: {model_name}")
        llm = create_llm(model_name)
        _llm_cache.set(model_name, llm)
    else:
        logger.debug(f"Using cached LLM instance: {model_name}")
    return llm


class LLMProvider:
    """Provider for LLM instances by agent role (cached with TTL)."""

    @staticmethod
    def get_pm_llm() -> LLM:
        return _get_or_create_llm(settings.llm_pm)

    @staticmethod
    def get_analyst_llm() -> LLM:
        return _get_or_create_llm(settings.llm_analyst)

    @staticmethod
    def get_architect_llm() -> LLM:
        return _get_or_create_llm(settings.llm_architect)

    @staticmethod
    def get_designer_llm() -> LLM:
        return _get_or_create_llm(settings.llm_designer)

    @staticmethod
    def get_developer_llm() -> LLM:
        return _get_or_create_llm(settings.llm_developer)

    @staticmethod
    def get_reviewer_llm() -> LLM:
        return _get_or_create_llm(settings.llm_reviewer)

    @staticmethod
    def get_qa_llm() -> LLM:
        return _get_or_create_llm(settings.llm_qa)

    @staticmethod
    def get_tech_writer_llm() -> LLM:
        return _get_or_create_llm(settings.llm_tech_writer)
    
    @staticmethod
    def clear_cache() -> None:
        """Clear the LLM cache manually."""
        _llm_cache.clear()
    
    @staticmethod
    def cache_size() -> int:
        """Get current cache size."""
        return _llm_cache.size()
