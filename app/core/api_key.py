"""
API Key utilities for generation, validation, and management.
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
import logging

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import APIKey, RateLimitTier
from app.database.postgres import db_manager

logger = logging.getLogger(__name__)


class APIKeyManager:
    """Manager class for API key operations."""

    # Default rate limits per tier
    RATE_LIMITS = {
        RateLimitTier.BASIC: {"requests_per_hour": 100, "requests_per_day": 2400},
        RateLimitTier.STANDARD: {"requests_per_hour": 1000, "requests_per_day": 24000},
        RateLimitTier.PREMIUM: {"requests_per_hour": 10000, "requests_per_day": 240000},
    }

    # Available scopes
    VALID_SCOPES = [
        "read:all",
        "read:pricing",
        "read:features",
        "read:testimonials",
        "read:faqs",
        "read:contact",
        "read:settings",
        "read:hero",
        "read:process",
        "read:addons",
        "read:onboarding",
        "write:content",
        "write:pricing",
        "write:features",
        "write:testimonials",
        "write:faqs",
        "write:contact",
        "write:settings",
        "write:hero",
        "write:process",
        "write:addons",
        "write:onboarding",
        "admin:full",
    ]

    @staticmethod
    def generate_api_key(environment: str = "live") -> Tuple[str, str, str]:
        """
        Generate a new API key.

        Args:
            environment: Environment prefix (live, test, dev)

        Returns:
            Tuple of (full_key, key_hash, key_prefix)
        """
        # Generate random key part (32 characters)
        key_part = secrets.token_urlsafe(24)  # ~32 chars after encoding

        # Create full key with prefix
        full_key = f"lx_{environment}_{key_part}"

        # Create display prefix (first 12 chars)
        key_prefix = full_key[:12] + "..."

        # Hash the full key for storage
        key_hash = hashlib.sha256(full_key.encode()).hexdigest()

        return full_key, key_hash, key_prefix

    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """Hash an API key for storage."""
        return hashlib.sha256(api_key.encode()).hexdigest()

    @staticmethod
    async def create_api_key(
        name: str,
        scopes: List[str],
        tier: RateLimitTier = RateLimitTier.BASIC,
        description: Optional[str] = None,
        expires_days: Optional[int] = None,
        ip_whitelist: Optional[List[str]] = None,
        created_by: Optional[str] = None,
        environment: str = "live"
    ) -> Tuple[APIKey, str]:
        """
        Create a new API key in the database.

        Args:
            name: Human-readable name for the key
            scopes: List of permission scopes
            tier: Rate limit tier
            description: Optional description
            expires_days: Days until expiration (None for no expiration)
            ip_whitelist: List of allowed IP addresses
            created_by: User who created the key
            environment: Environment (live, test, dev)

        Returns:
            Tuple of (APIKey model, raw_api_key)
        """
        # Validate scopes
        invalid_scopes = set(scopes) - set(APIKeyManager.VALID_SCOPES)
        if invalid_scopes:
            raise ValueError(f"Invalid scopes: {invalid_scopes}")

        # Generate API key
        full_key, key_hash, key_prefix = APIKeyManager.generate_api_key(environment)

        # Calculate expiration
        expires_at = None
        if expires_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_days)

        # Get rate limits for tier
        rate_limits = APIKeyManager.RATE_LIMITS[tier]

        # Create database record
        api_key = APIKey(
            key_hash=key_hash,
            key_prefix=key_prefix,
            name=name,
            description=description,
            scopes=scopes,
            rate_limit_tier=tier,
            requests_per_hour=rate_limits["requests_per_hour"],
            requests_per_day=rate_limits["requests_per_day"],
            ip_whitelist=ip_whitelist or [],
            expires_at=expires_at,
            created_by=created_by,
        )

        async with db_manager.get_session() as session:
            session.add(api_key)
            await session.commit()
            await session.refresh(api_key)

        logger.info(f"Created API key: {key_prefix} for {created_by or 'system'}")
        return api_key, full_key

    @staticmethod
    async def validate_api_key(api_key: str) -> Optional[APIKey]:
        """
        Validate an API key and return the associated record.

        Args:
            api_key: The raw API key

        Returns:
            APIKey model if valid, None otherwise
        """
        key_hash = APIKeyManager.hash_api_key(api_key)

        async with db_manager.get_session() as session:
            stmt = select(APIKey).where(
                APIKey.key_hash == key_hash,
                APIKey.is_active == True
            )
            result = await session.execute(stmt)
            api_key_record = result.scalar_one_or_none()

            if not api_key_record:
                return None

            # Check expiration
            if api_key_record.expires_at and datetime.utcnow() > api_key_record.expires_at:
                logger.warning(f"Expired API key used: {api_key_record.key_prefix}")
                return None

            # Update last used timestamp
            await session.execute(
                update(APIKey)
                .where(APIKey.id == api_key_record.id)
                .values(last_used_at=datetime.utcnow())
            )
            await session.commit()

            return api_key_record

    @staticmethod
    async def increment_request_count(api_key_id: str) -> None:
        """Increment the request count for an API key."""
        async with db_manager.get_session() as session:
            await session.execute(
                update(APIKey)
                .where(APIKey.id == api_key_id)
                .values(request_count=APIKey.request_count + 1)
            )
            await session.commit()

    @staticmethod
    async def revoke_api_key(api_key_id: str) -> bool:
        """
        Revoke (deactivate) an API key.

        Args:
            api_key_id: The API key ID to revoke

        Returns:
            True if revoked successfully, False if not found
        """
        async with db_manager.get_session() as session:
            result = await session.execute(
                update(APIKey)
                .where(APIKey.id == api_key_id)
                .values(is_active=False)
            )
            await session.commit()

            if result.rowcount > 0:
                logger.info(f"Revoked API key: {api_key_id}")
                return True
            return False

    @staticmethod
    async def list_api_keys(
        created_by: Optional[str] = None,
        is_active: Optional[bool] = None,
        tier: Optional[RateLimitTier] = None
    ) -> List[APIKey]:
        """
        List API keys with optional filters.

        Args:
            created_by: Filter by creator
            is_active: Filter by active status
            tier: Filter by rate limit tier

        Returns:
            List of APIKey models
        """
        async with db_manager.get_session() as session:
            stmt = select(APIKey)

            if created_by:
                stmt = stmt.where(APIKey.created_by == created_by)
            if is_active is not None:
                stmt = stmt.where(APIKey.is_active == is_active)
            if tier:
                stmt = stmt.where(APIKey.rate_limit_tier == tier)

            stmt = stmt.order_by(APIKey.created_at.desc())

            result = await session.execute(stmt)
            return result.scalars().all()

    @staticmethod
    def validate_scopes(scopes: List[str]) -> List[str]:
        """
        Validate and return invalid scopes.

        Args:
            scopes: List of scopes to validate

        Returns:
            List of invalid scopes
        """
        return list(set(scopes) - set(APIKeyManager.VALID_SCOPES))

    @staticmethod
    def check_scope_permission(api_key_scopes: List[str], required_scope: str) -> bool:
        """
        Check if API key has required scope permission.

        Args:
            api_key_scopes: Scopes assigned to the API key
            required_scope: Required scope for the operation

        Returns:
            True if permission granted, False otherwise
        """
        # Admin scope grants all permissions
        if "admin:full" in api_key_scopes:
            return True

        # Check for exact scope match
        if required_scope in api_key_scopes:
            return True

        # Check for wildcard permissions
        if required_scope.startswith("read:") and "read:all" in api_key_scopes:
            return True

        if required_scope.startswith("write:") and "write:content" in api_key_scopes:
            return True

        return False