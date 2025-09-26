"""
API key management endpoints.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field, validator

from app.core.api_key import APIKeyManager
from app.core.api_auth import require_admin_full, get_current_api_key
from app.models.database import APIKey, RateLimitTier

router = APIRouter(prefix="/api-keys", tags=["API Keys"])


# Pydantic schemas for API key management
class APIKeyCreate(BaseModel):
    """Schema for creating an API key."""
    name: str = Field(..., min_length=1, max_length=255, description="Human-readable name")
    description: Optional[str] = Field(None, max_length=1000, description="Optional description")
    scopes: List[str] = Field(..., min_items=1, description="List of permission scopes")
    tier: RateLimitTier = Field(RateLimitTier.BASIC, description="Rate limit tier")
    expires_days: Optional[int] = Field(None, gt=0, le=3650, description="Days until expiration")
    ip_whitelist: Optional[List[str]] = Field(None, description="Allowed IP addresses")
    environment: str = Field("live", description="Environment (live, test, dev)")

    @validator('scopes')
    def validate_scopes(cls, v):
        invalid_scopes = APIKeyManager.validate_scopes(v)
        if invalid_scopes:
            raise ValueError(f"Invalid scopes: {invalid_scopes}")
        return v

    @validator('environment')
    def validate_environment(cls, v):
        if v not in ['live', 'test', 'dev']:
            raise ValueError("Environment must be 'live', 'test', or 'dev'")
        return v


class APIKeyResponse(BaseModel):
    """Schema for API key response."""
    id: str
    key_prefix: str
    name: str
    description: Optional[str]
    scopes: List[str]
    rate_limit_tier: RateLimitTier
    requests_per_hour: int
    requests_per_day: int
    ip_whitelist: Optional[List[str]]
    is_active: bool
    last_used_at: Optional[datetime]
    request_count: int
    expires_at: Optional[datetime]
    created_by: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class APIKeyCreateResponse(BaseModel):
    """Schema for API key creation response."""
    api_key: APIKeyResponse
    raw_key: str = Field(..., description="The actual API key (only shown once)")
    message: str = "API key created successfully. Save this key securely - it won't be shown again."


class APIKeyUpdate(BaseModel):
    """Schema for updating an API key."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    scopes: Optional[List[str]] = Field(None, min_items=1)
    tier: Optional[RateLimitTier] = None
    ip_whitelist: Optional[List[str]] = None
    is_active: Optional[bool] = None

    @validator('scopes')
    def validate_scopes(cls, v):
        if v is not None:
            invalid_scopes = APIKeyManager.validate_scopes(v)
            if invalid_scopes:
                raise ValueError(f"Invalid scopes: {invalid_scopes}")
        return v


class APIKeyList(BaseModel):
    """Schema for listing API keys."""
    keys: List[APIKeyResponse]
    total: int
    page: int
    size: int


class RateLimitStatus(BaseModel):
    """Schema for rate limit status."""
    hour_count: int
    day_count: int
    hour_limit: int
    day_limit: int
    hour_remaining: int
    day_remaining: int
    hour_reset: int
    day_reset: int


# Endpoints
@router.post("/", response_model=APIKeyCreateResponse)
async def create_api_key(
    key_data: APIKeyCreate,
    current_user = Depends(require_admin_full)
):
    """
    Create a new API key.

    **Requires admin:full scope**

    The raw API key is only returned once during creation.
    Store it securely as it cannot be retrieved again.
    """
    try:
        # Get created_by from current auth context
        created_by = None
        if hasattr(current_user, 'email'):
            created_by = current_user.email
        elif hasattr(current_user, 'key_prefix'):
            created_by = f"api_key:{current_user.key_prefix}"

        api_key, raw_key = await APIKeyManager.create_api_key(
            name=key_data.name,
            scopes=key_data.scopes,
            tier=key_data.tier,
            description=key_data.description,
            expires_days=key_data.expires_days,
            ip_whitelist=key_data.ip_whitelist,
            created_by=created_by,
            environment=key_data.environment
        )

        return APIKeyCreateResponse(
            api_key=APIKeyResponse.from_orm(api_key),
            raw_key=raw_key
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create API key: {str(e)}"
        )


@router.get("/", response_model=List[APIKeyResponse])
async def list_api_keys(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    tier: Optional[RateLimitTier] = Query(None, description="Filter by rate limit tier"),
    created_by: Optional[str] = Query(None, description="Filter by creator"),
    current_user = Depends(require_admin_full)
):
    """
    List all API keys.

    **Requires admin:full scope**
    """
    try:
        api_keys = await APIKeyManager.list_api_keys(
            created_by=created_by,
            is_active=is_active,
            tier=tier
        )

        return [APIKeyResponse.from_orm(key) for key in api_keys]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list API keys: {str(e)}"
        )


@router.get("/{key_id}", response_model=APIKeyResponse)
async def get_api_key(
    key_id: str,
    current_user = Depends(require_admin_full)
):
    """
    Get a specific API key by ID.

    **Requires admin:full scope**
    """
    try:
        api_keys = await APIKeyManager.list_api_keys()
        api_key = next((key for key in api_keys if str(key.id) == key_id), None)

        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )

        return APIKeyResponse.from_orm(api_key)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get API key: {str(e)}"
        )


@router.patch("/{key_id}", response_model=APIKeyResponse)
async def update_api_key(
    key_id: str,
    key_update: APIKeyUpdate,
    current_user = Depends(require_admin_full)
):
    """
    Update an API key.

    **Requires admin:full scope**

    Note: Cannot update key_hash, key_prefix, or created_at.
    """
    try:
        # This would need to be implemented in APIKeyManager
        # For now, return not implemented
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="API key updates not yet implemented"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update API key: {str(e)}"
        )


@router.delete("/{key_id}")
async def revoke_api_key(
    key_id: str,
    current_user = Depends(require_admin_full)
):
    """
    Revoke (deactivate) an API key.

    **Requires admin:full scope**

    This sets is_active=False. The key cannot be reactivated.
    """
    try:
        success = await APIKeyManager.revoke_api_key(key_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )

        return {"message": "API key revoked successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to revoke API key: {str(e)}"
        )


@router.get("/{key_id}/rate-limit-status", response_model=RateLimitStatus)
async def get_rate_limit_status(
    key_id: str,
    current_user = Depends(require_admin_full)
):
    """
    Get current rate limit status for an API key.

    **Requires admin:full scope**
    """
    try:
        # Get API key details
        api_keys = await APIKeyManager.list_api_keys()
        api_key = next((key for key in api_keys if str(key.id) == key_id), None)

        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )

        from app.core.rate_limiting import api_key_rate_limiter

        status = await api_key_rate_limiter.get_rate_limit_status(
            key_identifier=key_id,
            requests_per_hour=api_key.requests_per_hour,
            requests_per_day=api_key.requests_per_day
        )

        return RateLimitStatus(**status)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get rate limit status: {str(e)}"
        )


@router.get("/scopes/available")
async def list_available_scopes(
    current_user = Depends(require_admin_full)
):
    """
    List all available API key scopes.

    **Requires admin:full scope**
    """
    return {
        "scopes": APIKeyManager.VALID_SCOPES,
        "total": len(APIKeyManager.VALID_SCOPES),
        "categories": {
            "read": [s for s in APIKeyManager.VALID_SCOPES if s.startswith("read:")],
            "write": [s for s in APIKeyManager.VALID_SCOPES if s.startswith("write:")],
            "admin": [s for s in APIKeyManager.VALID_SCOPES if s.startswith("admin:")]
        }
    }


@router.get("/tiers/available")
async def list_available_tiers(
    current_user = Depends(require_admin_full)
):
    """
    List all available rate limit tiers with their limits.

    **Requires admin:full scope**
    """
    return {
        "tiers": {
            tier.value: {
                "name": tier.value,
                "requests_per_hour": limits["requests_per_hour"],
                "requests_per_day": limits["requests_per_day"]
            }
            for tier, limits in APIKeyManager.RATE_LIMITS.items()
        }
    }


# Current API key info endpoint (for API key users to check their own status)
@router.get("/me/info", response_model=APIKeyResponse)
async def get_my_api_key_info(
    current_api_key: APIKey = Depends(get_current_api_key)
):
    """
    Get information about the current API key.

    **Requires valid API key**

    Allows API key users to check their own key status and limits.
    """
    if not current_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Valid API key required"
        )

    return APIKeyResponse.from_orm(current_api_key)


@router.get("/me/rate-limit-status", response_model=RateLimitStatus)
async def get_my_rate_limit_status(
    current_api_key: APIKey = Depends(get_current_api_key)
):
    """
    Get current rate limit status for the current API key.

    **Requires valid API key**
    """
    if not current_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Valid API key required"
        )

    try:
        from app.core.rate_limiting import api_key_rate_limiter

        status = await api_key_rate_limiter.get_rate_limit_status(
            key_identifier=current_api_key.id,
            requests_per_hour=current_api_key.requests_per_hour,
            requests_per_day=current_api_key.requests_per_day
        )

        return RateLimitStatus(**status)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get rate limit status: {str(e)}"
        )