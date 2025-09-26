"""
API Key Authentication middleware and dependencies.
"""

import logging
from typing import Optional, List
from fastapi import Request, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.api_key import APIKeyManager
from app.core.rate_limiting import api_key_rate_limiter
from app.models.database import APIKey

logger = logging.getLogger(__name__)

# HTTP Bearer scheme for API keys
security = HTTPBearer(auto_error=False)


class APIKeyAuthMiddleware(BaseHTTPMiddleware):
    """Middleware to handle API key authentication and rate limiting."""

    def __init__(self, app):
        super().__init__(app)
        self.api_key_manager = APIKeyManager()

    async def dispatch(self, request: Request, call_next):
        """Process request with API key authentication."""

        # Skip auth for certain paths
        skip_paths = [
            "/",
            "/health",
            "/api/v1/docs",
            "/api/v1/redoc",
            "/api/v1/openapi.json",
            "/api/v1/auth/login",
            "/api/v1/auth/logout"
        ]

        if request.url.path in skip_paths:
            return await call_next(request)

        # Extract API key from request
        api_key = await self._extract_api_key(request)

        if api_key:
            try:
                # Validate API key
                api_key_record = await APIKeyManager.validate_api_key(api_key)

                if not api_key_record:
                    logger.warning(f"Invalid API key used from IP: {request.client.host}")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid API key",
                        headers={"WWW-Authenticate": "Bearer"}
                    )

                # Check IP whitelist if configured
                if api_key_record.ip_whitelist and request.client.host not in api_key_record.ip_whitelist:
                    logger.warning(
                        f"API key {api_key_record.key_prefix} used from unauthorized IP: {request.client.host}"
                    )
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="API key not authorized for this IP address"
                    )

                # Check rate limits
                rate_limit_status = await api_key_rate_limiter.check_rate_limit(
                    key_identifier=api_key_record.id,
                    requests_per_hour=api_key_record.requests_per_hour,
                    requests_per_day=api_key_record.requests_per_day,
                    api_key_id=api_key_record.id
                )

                # Store API key info in request state
                request.state.api_key = api_key_record
                request.state.rate_limit_status = rate_limit_status
                request.state.auth_type = "api_key"

                # Increment request count (async)
                try:
                    await APIKeyManager.increment_request_count(api_key_record.id)
                except Exception as e:
                    logger.error(f"Failed to increment request count: {e}")

            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"API key validation error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Authentication service temporarily unavailable"
                )
        else:
            # No API key provided, continue with normal JWT auth
            request.state.auth_type = "jwt"

        # Process request
        response = await call_next(request)

        # Add rate limit headers if API key was used
        if hasattr(request.state, 'rate_limit_status'):
            rate_status = request.state.rate_limit_status
            if 'hour_limit' in rate_status:
                response.headers["X-RateLimit-Limit"] = str(rate_status['hour_limit'])
                response.headers["X-RateLimit-Remaining"] = str(rate_status['hour_remaining'])
                response.headers["X-RateLimit-Reset"] = str(rate_status['hour_reset'])
                response.headers["X-RateLimit-Limit-Daily"] = str(rate_status['day_limit'])
                response.headers["X-RateLimit-Remaining-Daily"] = str(rate_status['day_remaining'])

        return response

    async def _extract_api_key(self, request: Request) -> Optional[str]:
        """Extract API key from request headers."""

        # Try X-API-Key header first
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return api_key

        # Try Authorization header
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            # Check if it's an API key (starts with lx_)
            if token.startswith("lx_"):
                return token

        return None


# Dependency functions for FastAPI endpoints
async def get_current_api_key(request: Request) -> Optional[APIKey]:
    """Get current API key from request state."""
    return getattr(request.state, 'api_key', None)


async def require_api_key(request: Request) -> APIKey:
    """Require a valid API key for the endpoint."""
    api_key = await get_current_api_key(request)
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return api_key


def require_scopes(required_scopes: List[str]):
    """
    Dependency factory to require specific scopes.

    Args:
        required_scopes: List of required scopes

    Returns:
        FastAPI dependency function
    """
    async def check_scopes(api_key: APIKey = Depends(require_api_key)) -> APIKey:
        for scope in required_scopes:
            if not APIKeyManager.check_scope_permission(api_key.scopes, scope):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required scope: {scope}"
                )
        return api_key

    return check_scopes


def require_scope(required_scope: str):
    """
    Dependency factory to require a single scope.

    Args:
        required_scope: Required scope

    Returns:
        FastAPI dependency function
    """
    return require_scopes([required_scope])


# Common scope dependencies
require_read_all = require_scope("read:all")
require_write_content = require_scope("write:content")
require_admin_full = require_scope("admin:full")

# Specific endpoint scopes
require_read_pricing = require_scope("read:pricing")
require_write_pricing = require_scope("write:pricing")
require_read_features = require_scope("read:features")
require_write_features = require_scope("write:features")
require_read_testimonials = require_scope("read:testimonials")
require_write_testimonials = require_scope("write:testimonials")


# Alternative authentication (API key OR JWT)
async def get_current_user_or_api_key(request: Request):
    """Get current user from JWT or API key authentication."""
    auth_type = getattr(request.state, 'auth_type', 'jwt')

    if auth_type == 'api_key':
        return await get_current_api_key(request)
    else:
        # This will integrate with existing JWT auth system
        # For now, return None to indicate JWT should be checked
        return None


def optional_api_key_auth(request: Request) -> Optional[APIKey]:
    """Optional API key authentication that doesn't raise errors."""
    return getattr(request.state, 'api_key', None)


# Rate limit info dependency
async def get_rate_limit_status(request: Request) -> dict:
    """Get current rate limit status from request."""
    return getattr(request.state, 'rate_limit_status', {})


# Security utility functions
def check_ip_whitelist(api_key: APIKey, client_ip: str) -> bool:
    """Check if client IP is in API key whitelist."""
    if not api_key.ip_whitelist:
        return True  # No whitelist means all IPs allowed
    return client_ip in api_key.ip_whitelist


def is_api_key_expired(api_key: APIKey) -> bool:
    """Check if API key is expired."""
    if not api_key.expires_at:
        return False  # No expiration
    from datetime import datetime
    return datetime.utcnow() > api_key.expires_at


# Logging utilities
def log_api_key_usage(api_key: APIKey, request: Request, response_status: int):
    """Log API key usage for monitoring."""
    logger.info(
        f"API Key Usage - Key: {api_key.key_prefix}, "
        f"IP: {request.client.host}, "
        f"Method: {request.method}, "
        f"Path: {request.url.path}, "
        f"Status: {response_status}, "
        f"User-Agent: {request.headers.get('User-Agent', 'Unknown')}"
    )