"""
Rate limiting functionality using slowapi and Redis.
"""

import time
import json
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import redis.asyncio as redis
import logging

from app.core.cache import redis_client
from app.models.database import RateLimitTier

logger = logging.getLogger(__name__)


class APIKeyRateLimiter:
    """Custom rate limiter for API keys with Redis backend."""

    def __init__(self):
        self.redis = redis_client

    async def check_rate_limit(
        self,
        key_identifier: str,
        requests_per_hour: int,
        requests_per_day: int,
        api_key_id: str
    ) -> Dict[str, Any]:
        """
        Check rate limits for an API key.

        Args:
            key_identifier: Unique identifier for the API key
            requests_per_hour: Hourly request limit
            requests_per_day: Daily request limit
            api_key_id: API key ID for logging

        Returns:
            Dict with rate limit status and metadata

        Raises:
            HTTPException: If rate limit exceeded
        """
        current_time = int(time.time())
        hour_window = current_time // 3600  # Current hour
        day_window = current_time // 86400   # Current day

        # Redis keys for tracking
        hour_key = f"rate_limit:hour:{key_identifier}:{hour_window}"
        day_key = f"rate_limit:day:{key_identifier}:{day_window}"

        try:
            # Get current counts
            pipe = self.redis.pipeline()
            pipe.get(hour_key)
            pipe.get(day_key)
            results = await pipe.execute()

            hour_count = int(results[0] or 0)
            day_count = int(results[1] or 0)

            # Check limits
            if hour_count >= requests_per_hour:
                reset_time = (hour_window + 1) * 3600
                logger.warning(f"Hourly rate limit exceeded for API key {api_key_id}")
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "Rate limit exceeded",
                        "limit_type": "hourly",
                        "limit": requests_per_hour,
                        "used": hour_count,
                        "reset_at": reset_time,
                        "retry_after": reset_time - current_time
                    },
                    headers={
                        "X-RateLimit-Limit": str(requests_per_hour),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(reset_time),
                        "Retry-After": str(reset_time - current_time)
                    }
                )

            if day_count >= requests_per_day:
                reset_time = (day_window + 1) * 86400
                logger.warning(f"Daily rate limit exceeded for API key {api_key_id}")
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "Rate limit exceeded",
                        "limit_type": "daily",
                        "limit": requests_per_day,
                        "used": day_count,
                        "reset_at": reset_time,
                        "retry_after": reset_time - current_time
                    },
                    headers={
                        "X-RateLimit-Limit-Daily": str(requests_per_day),
                        "X-RateLimit-Remaining-Daily": str(requests_per_day - day_count),
                        "X-RateLimit-Reset-Daily": str(reset_time),
                        "Retry-After": str(reset_time - current_time)
                    }
                )

            # Increment counters
            pipe = self.redis.pipeline()
            pipe.incr(hour_key)
            pipe.expire(hour_key, 3600)  # Expire after 1 hour
            pipe.incr(day_key)
            pipe.expire(day_key, 86400)  # Expire after 1 day
            await pipe.execute()

            # Return status
            return {
                "allowed": True,
                "hour_count": hour_count + 1,
                "day_count": day_count + 1,
                "hour_limit": requests_per_hour,
                "day_limit": requests_per_day,
                "hour_remaining": requests_per_hour - (hour_count + 1),
                "day_remaining": requests_per_day - (day_count + 1),
                "hour_reset": (hour_window + 1) * 3600,
                "day_reset": (day_window + 1) * 86400
            }

        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            logger.error(f"Rate limiting error for API key {api_key_id}: {e}")
            # Allow request if Redis is down (fail open)
            return {
                "allowed": True,
                "error": "Rate limiting temporarily unavailable",
                "hour_count": 0,
                "day_count": 0,
                "hour_limit": requests_per_hour,
                "day_limit": requests_per_day
            }

    async def get_rate_limit_status(
        self,
        key_identifier: str,
        requests_per_hour: int,
        requests_per_day: int
    ) -> Dict[str, Any]:
        """
        Get current rate limit status without incrementing counters.

        Args:
            key_identifier: Unique identifier for the API key
            requests_per_hour: Hourly request limit
            requests_per_day: Daily request limit

        Returns:
            Dict with current rate limit status
        """
        current_time = int(time.time())
        hour_window = current_time // 3600
        day_window = current_time // 86400

        hour_key = f"rate_limit:hour:{key_identifier}:{hour_window}"
        day_key = f"rate_limit:day:{key_identifier}:{day_window}"

        try:
            pipe = self.redis.pipeline()
            pipe.get(hour_key)
            pipe.get(day_key)
            results = await pipe.execute()

            hour_count = int(results[0] or 0)
            day_count = int(results[1] or 0)

            return {
                "hour_count": hour_count,
                "day_count": day_count,
                "hour_limit": requests_per_hour,
                "day_limit": requests_per_day,
                "hour_remaining": max(0, requests_per_hour - hour_count),
                "day_remaining": max(0, requests_per_day - day_count),
                "hour_reset": (hour_window + 1) * 3600,
                "day_reset": (day_window + 1) * 86400
            }
        except Exception as e:
            logger.error(f"Error getting rate limit status: {e}")
            return {
                "hour_count": 0,
                "day_count": 0,
                "hour_limit": requests_per_hour,
                "day_limit": requests_per_day,
                "error": "Rate limiting temporarily unavailable"
            }


# Global rate limiter instance
api_key_rate_limiter = APIKeyRateLimiter()


# Standard rate limiter for IP-based limiting (fallback)
def get_rate_limit_key(request: Request) -> str:
    """Get rate limit key from request (IP + API key if available)."""
    # Try to get API key from headers
    api_key = request.headers.get("X-API-Key") or None
    if not api_key:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            # Simple check if it's an API key (starts with lx_)
            if token.startswith("lx_"):
                api_key = token

    # Use API key prefix if available, otherwise use IP
    if api_key:
        return f"apikey:{api_key[:12]}"
    else:
        return f"ip:{get_remote_address(request)}"


# Standard slowapi limiter for IP-based rate limiting
limiter = Limiter(key_func=get_rate_limit_key)


# Rate limit tiers configuration
TIER_LIMITS = {
    RateLimitTier.BASIC: "100/hour",
    RateLimitTier.STANDARD: "1000/hour",
    RateLimitTier.PREMIUM: "10000/hour"
}


def get_tier_limit(tier: RateLimitTier) -> str:
    """Get rate limit string for a tier."""
    return TIER_LIMITS.get(tier, "100/hour")


# Custom rate limit decorator for API keys
def api_key_rate_limit(tier: Optional[RateLimitTier] = None):
    """
    Decorator for API key-based rate limiting.

    Args:
        tier: Rate limit tier (if None, will be determined from API key)
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # This will be implemented in the middleware
            # The decorator is for documentation purposes
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# Exception handler for rate limit exceeded
async def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded) -> HTTPException:
    """Custom handler for rate limit exceeded errors."""
    response = {
        "error": "Rate limit exceeded",
        "detail": f"Rate limit exceeded: {exc.detail}",
        "type": "rate_limit_error"
    }

    logger.warning(f"Rate limit exceeded for {get_rate_limit_key(request)}: {exc.detail}")

    return HTTPException(
        status_code=429,
        detail=response,
        headers={"Retry-After": "60"}  # Default retry after 1 minute
    )