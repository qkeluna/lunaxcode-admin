"""
Site settings API endpoints.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
# Caching temporarily disabled for deployment

from app.database.xata import get_database, XataDB
from app.models.content import SiteSetting, SiteSettingCreate, SiteSettingUpdate
from app.models.base import PaginationParams, PaginatedResponse, BaseResponse
from app.services.base import BaseService
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


def get_site_settings_service(db: XataDB = Depends(get_database)) -> BaseService:
    return BaseService(
        db=db,
        table_name="site_settings",
        model_class=SiteSetting,
        create_model_class=SiteSettingCreate,
        update_model_class=SiteSettingUpdate
    )


@router.post("/", response_model=SiteSetting, status_code=status.HTTP_201_CREATED)
async def create_site_setting(
    data: SiteSettingCreate,
    service: BaseService = Depends(get_site_settings_service)
) -> SiteSetting:
    return await service.create(data)


@router.get("/", response_model=PaginatedResponse)
# @cache(expire=settings.CACHE_TTL)
async def get_site_settings(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    public_only: bool = Query(False),
    service: BaseService = Depends(get_site_settings_service)
) -> PaginatedResponse:
    pagination = PaginationParams(page=page, size=size)
    filter_conditions = {"isPublic": True} if public_only else None
    
    return await service.get_all(
        pagination=pagination,
        filter_conditions=filter_conditions,
        sort_by="key"
    )


@router.get("/key/{key}", response_model=SiteSetting)
# @cache(expire=settings.CACHE_TTL)
async def get_site_setting_by_key(
    key: str,
    service: BaseService = Depends(get_site_settings_service)
) -> SiteSetting:
    # Query by key field
    try:
        result = await service.db.query_records(
            table="site_settings",
            filter_conditions={"key": key},
            page_size=1
        )
        records = result.get("records", [])
        if not records:
            raise HTTPException(status_code=404, detail=f"Setting with key '{key}' not found")
        return SiteSetting(**records[0])
    except Exception as e:
        logger.error(f"Error getting setting by key {key}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve setting")


@router.get("/{record_id}", response_model=SiteSetting)
# @cache(expire=settings.CACHE_TTL)
async def get_site_setting(
    record_id: str,
    service: BaseService = Depends(get_site_settings_service)
) -> SiteSetting:
    result = await service.get_by_id(record_id)
    if not result:
        raise HTTPException(status_code=404, detail="Site setting not found")
    return result


@router.patch("/{record_id}", response_model=SiteSetting)
async def update_site_setting(
    record_id: str,
    data: SiteSettingUpdate,
    service: BaseService = Depends(get_site_settings_service)
) -> SiteSetting:
    return await service.update(record_id, data)


@router.delete("/{record_id}", response_model=BaseResponse)
async def delete_site_setting(
    record_id: str,
    service: BaseService = Depends(get_site_settings_service)
) -> BaseResponse:
    await service.delete(record_id)
    return BaseResponse(success=True, message="Site setting deleted permanently")
