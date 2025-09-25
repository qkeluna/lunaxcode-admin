"""
Site settings API endpoints.
"""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db_session
from app.models.schemas import SiteSetting, SiteSettingCreate, SiteSettingUpdate, PaginationParams, PaginatedResponse, BaseResponse
from app.models.database import SettingType
from app.services.postgres_services import PostgresSiteSettingsService
from app.core.exceptions import NotFoundError, ValidationException
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


def get_service(session: AsyncSession = Depends(get_db_session)) -> PostgresSiteSettingsService:
    """Get service instance."""
    return PostgresSiteSettingsService(session)


@router.post(
    "/",
    response_model=SiteSetting,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new site setting"
)
async def create_site_setting(
    setting_data: SiteSettingCreate,
    service: PostgresSiteSettingsService = Depends(get_service)
) -> SiteSetting:
    """Create a new site setting."""
    try:
        return await service.create(setting_data)
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.detail
        )
    except Exception as e:
        logger.error(f"Error creating site setting: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create site setting"
        )


@router.get(
    "/",
    response_model=PaginatedResponse,
    summary="Get all site settings"
)
async def get_site_settings(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    public_only: bool = Query(False, description="Get only public settings"),
    service: PostgresSiteSettingsService = Depends(get_service)
) -> PaginatedResponse:
    """Get all site settings with pagination."""
    try:
        pagination = PaginationParams(page=page, size=size)
        filters = {}
        if public_only:
            filters["is_public"] = True
        
        return await service.get_all(
            pagination=pagination,
            filters=filters or None
        )
    except Exception as e:
        logger.error(f"Error getting site settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve site settings"
        )


@router.get(
    "/public",
    response_model=List[SiteSetting],
    summary="Get public site settings"
)
async def get_public_site_settings(
    service: PostgresSiteSettingsService = Depends(get_service)
) -> List[SiteSetting]:
    """Get all public site settings."""
    try:
        return await service.get_public_settings()
    except Exception as e:
        logger.error(f"Error getting public site settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve public site settings"
        )


@router.get(
    "/key/{key}",
    response_model=SiteSetting,
    summary="Get site setting by key"
)
async def get_site_setting_by_key(
    key: str,
    service: PostgresSiteSettingsService = Depends(get_service)
) -> SiteSetting:
    """Get site setting by key."""
    try:
        setting = await service.get_by_key(key)
        if not setting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Site setting with key '{key}' not found"
            )
        return setting
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting site setting by key {key}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve site setting"
        )


@router.get(
    "/{record_id}",
    response_model=SiteSetting,
    summary="Get site setting by ID"
)
async def get_site_setting(
    record_id: str,
    service: PostgresSiteSettingsService = Depends(get_service)
) -> SiteSetting:
    """Get site setting by ID."""
    try:
        setting = await service.get_by_id(record_id)
        if not setting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Site setting with ID '{record_id}' not found"
            )
        return setting
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting site setting {record_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve site setting"
        )


@router.patch(
    "/{record_id}",
    response_model=SiteSetting,
    summary="Update site setting"
)
async def update_site_setting(
    record_id: str,
    setting_data: SiteSettingUpdate,
    service: PostgresSiteSettingsService = Depends(get_service)
) -> SiteSetting:
    """Update site setting."""
    try:
        return await service.update(record_id, setting_data)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail
        )
    except Exception as e:
        logger.error(f"Error updating site setting {record_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update site setting"
        )


@router.delete(
    "/{record_id}",
    response_model=BaseResponse,
    summary="Delete site setting"
)
async def delete_site_setting(
    record_id: str,
    service: PostgresSiteSettingsService = Depends(get_service)
) -> BaseResponse:
    """Delete site setting."""
    try:
        success = await service.delete(record_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Site setting with ID '{record_id}' not found"
            )
        
        return BaseResponse(success=True, message="Site setting deleted permanently")
    except HTTPException:
        raise
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail
        )
    except Exception as e:
        logger.error(f"Error deleting site setting {record_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete site setting"
        )