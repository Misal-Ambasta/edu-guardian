
"""Cache Service module for the application.

This module provides functionality related to cache service.
"""
from typing import Any, Optional, Dict, List, Union, Callable
import json
import os
import redis
import functools
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class CacheService:
    """Service for caching frequent operations using Redis"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CacheService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize Redis connection"""
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.redis = redis.from_url(redis_url)
        self.default_ttl = int(os.getenv("CACHE_TTL", 3600))  # Default: 1 hour

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        value = self.redis.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value.decode('utf-8')
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL"""
        if ttl is None:
            ttl = self.default_ttl

        try:
            serialized_value = json.dumps(value)
            return self.redis.setex(key, ttl, serialized_value)
        except (TypeError, json.JSONDecodeError):
            # For non-serializable objects, store as string
            return self.redis.setex(key, ttl, str(value))

    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        return bool(self.redis.delete(key))

    def flush(self) -> bool:
        """Flush all cache"""
        return self.redis.flushdb()


def cached(ttl: Optional[int] = None, key_prefix: str = ""):
    """Decorator for caching function results"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{hash(
                str(args) + str(sorted(kwargs.items())))}"

            # Get cache service
            cache = CacheService()

            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache.set(cache_key, result, ttl)

            return result
        return wrapper
    return decorator


def invalidate_cache(key_pattern: str):
    """Decorator for invalidating cache after function execution"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)

            # Invalidate cache
            cache = CacheService()
            keys = cache.redis.keys(key_pattern)
            if keys:
                cache.redis.delete(*keys)

            return result
        return wrapper
    return decorator
