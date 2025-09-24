"""
Redis cache configuration and utilities.
"""

import json
import logging
from typing import Any, Optional, Dict
import redis.asyncio as redis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from app.core.config import settings

logger = logging.getLogger(__name__)

# Redis client
redis_client: Optional[redis.Redis] = None


async def init_cache():
    """Initialize Redis cache."""
    global redis_client
    
    try:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        
        # Test connection
        await redis_client.ping()
        
        # Initialize FastAPI Cache with Redis
        FastAPICache.init(RedisBackend(redis_client), prefix="lunaxcode-cms")
        
        logger.info("✅ Redis cache initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize Redis cache: {e}")
        redis_client = None
        
        # Initialize FastAPICache with a dummy backend to prevent errors
        from fastapi_cache.backends.inmemory import InMemoryBackend
        FastAPICache.init(InMemoryBackend(), prefix="lunaxcode-cms")
        logger.info("✅ FastAPI Cache initialized with in-memory backend (fallback)")


async def get_cache(key: str) -> Optional[Dict[str, Any]]:
    """Get value from cache."""
    if not redis_client:
        return None
    
    try:
        value = await redis_client.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception as e:
        logger.error(f"Cache get error for key {key}: {e}")
        return None


async def set_cache(key: str, value: Dict[str, Any], ttl: int = None) -> bool:
    """Set value in cache."""
    if not redis_client:
        return False
    
    try:
        ttl = ttl or settings.CACHE_TTL
        await redis_client.setex(
            key,
            ttl,
            json.dumps(value, default=str)
        )
        return True
    except Exception as e:
        logger.error(f"Cache set error for key {key}: {e}")
        return False


async def delete_cache(key: str) -> bool:
    """Delete value from cache."""
    if not redis_client:
        return False
    
    try:
        await redis_client.delete(key)
        return True
    except Exception as e:
        logger.error(f"Cache delete error for key {key}: {e}")
        return False


async def delete_cache_pattern(pattern: str) -> int:
    """Delete all keys matching pattern."""
    if not redis_client:
        return 0
    
    try:
        keys = await redis_client.keys(pattern)
        if keys:
            deleted = await redis_client.delete(*keys)
            return deleted
        return 0
    except Exception as e:
        logger.error(f"Cache pattern delete error for pattern {pattern}: {e}")
        return 0


def cache_key_builder(
    func_name: str,
    table: str = None,
    identifier: str = None,
    **kwargs
) -> str:
    """Build cache key for function calls."""
    key_parts = ["lunaxcode-cms", func_name]
    
    if table:
        key_parts.append(table)
    
    if identifier:
        key_parts.append(str(identifier))
    
    if kwargs:
        # Sort kwargs for consistent keys
        sorted_kwargs = sorted(kwargs.items())
        params = "_".join([f"{k}:{v}" for k, v in sorted_kwargs])
        key_parts.append(params)
    
    return ":".join(key_parts)
