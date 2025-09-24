"""
Addon services API endpoints.
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_cache2.decorator import cache

from app.database.xata import get_database, XataDB
from app.models.content import AddonService, AddonServiceCreate, AddonServiceUpdate, ServiceCategory
from app.models.base import PaginationParams, PaginatedResponse, BaseResponse
from app.services.base import BaseService
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


def get_addon_services_service(db: XataDB = Depends(get_database)) -> BaseService:
    return BaseService(
        db=db,
        table_name="addon_services",
        model_class=AddonService,
        create_model_class=AddonServiceCreate,
        update_model_class=AddonServiceUpdate
    )


@router.post("/", response_model=AddonService, status_code=status.HTTP_201_CREATED)
async def create_addon_service(
    data: AddonServiceCreate,
    service: BaseService = Depends(get_addon_services_service)
) -> AddonService:
    return await service.create(data)


@router.get("/", response_model=PaginatedResponse)
@cache(expire=settings.CACHE_TTL)
async def get_addon_services(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    category: Optional[ServiceCategory] = Query(None),
    popular_only: bool = Query(False),
    active_only: bool = Query(True),
    service: BaseService = Depends(get_addon_services_service)
) -> PaginatedResponse:
    pagination = PaginationParams(page=page, size=size)
    filter_conditions = {}
    
    if active_only:
        filter_conditions["isActive"] = True
    if category:
        filter_conditions["category"] = category.value
    if popular_only:
        filter_conditions["popular"] = True
    
    return await service.get_all(
        pagination=pagination,
        filter_conditions=filter_conditions if filter_conditions else None
    )


@router.get("/service-id/{service_id}", response_model=AddonService)
@cache(expire=settings.CACHE_TTL)
async def get_addon_service_by_service_id(
    service_id: str,
    service: BaseService = Depends(get_addon_services_service)
) -> AddonService:
    try:
        result = await service.db.query_records(
            table="addon_services",
            filter_conditions={"serviceId": service_id},
            page_size=1
        )
        records = result.get("records", [])
        if not records:
            raise HTTPException(status_code=404, detail=f"Service with serviceId '{service_id}' not found")
        return AddonService(**records[0])
    except Exception as e:
        logger.error(f"Error getting service by serviceId {service_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve service")


@router.get("/{record_id}", response_model=AddonService)
@cache(expire=settings.CACHE_TTL)
async def get_addon_service(
    record_id: str,
    service: BaseService = Depends(get_addon_services_service)
) -> AddonService:
    result = await service.get_by_id(record_id)
    if not result:
        raise HTTPException(status_code=404, detail="Addon service not found")
    return result


@router.patch("/{record_id}", response_model=AddonService)
async def update_addon_service(
    record_id: str,
    data: AddonServiceUpdate,
    service: BaseService = Depends(get_addon_services_service)
) -> AddonService:
    return await service.update(record_id, data)


@router.delete("/{record_id}", response_model=BaseResponse)
async def delete_addon_service(
    record_id: str,
    hard_delete: bool = Query(False),
    service: BaseService = Depends(get_addon_services_service)
) -> BaseResponse:
    if hard_delete:
        await service.delete(record_id)
        message = "Addon service deleted permanently"
    else:
        await service.update(record_id, AddonServiceUpdate(isActive=False))
        message = "Addon service deactivated"
    return BaseResponse(success=True, message=message)
