"""
Cache Manager
Provides caching utilities for data fetching
"""

from typing import Any, Callable, Optional
from functools import wraps
from cachetools import TTLCache
import logging

logger = logging.getLogger(__name__)

# Global cache instance
_cache: Optional[TTLCache] = None


def get_cache_manager() -> TTLCache:
    """
    Get or create the global cache manager
    
    Returns:
        TTLCache instance
    """
    global _cache
    if _cache is None:
        _cache = TTLCache(maxsize=256, ttl=900)  # 15 minutes default
    return _cache


def cache_result(key_prefix: str = "", ttl: int = 900):
    """
    Decorator to cache function results
    
    Args:
        key_prefix: Prefix for cache keys
        ttl: Time to live in seconds
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        cache = TTLCache(maxsize=256, ttl=ttl)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"
            
            if cache_key in cache:
                logger.debug(f"Cache hit for {func.__name__}")
                return cache[cache_key]
            
            result = func(*args, **kwargs)
            cache[cache_key] = result
            return result
        
        return wrapper
    return decorator

