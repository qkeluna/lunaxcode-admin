"""
Contact info API endpoints.
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
# Caching temporarily disabled for deployment

from app.database.xata import get_database, XataDB
from app.models.content import ContactInfo, ContactInfoCreate, ContactInfoUpdate, ContactType
from app.models.base import PaginationParams, PaginatedResponse, BaseResponse
from app.services.base import BaseService
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


def get_contact_info_service(db: XataDB = Depends(get_database)) -> BaseService:
    return BaseService(
        db=db,
        table_name="contact_info",
        model_class=ContactInfo,
        create_model_class=ContactInfoCreate,
        update_model_class=ContactInfoUpdate
    )


@router.post("/", response_model=ContactInfo, status_code=status.HTTP_201_CREATED)
async def create_contact_info(
    data: ContactInfoCreate,
    service: BaseService = Depends(get_contact_info_service)
) -> ContactInfo:
    return await service.create(data)


@router.get("/", response_model=PaginatedResponse)
# @cache(expire=settings.CACHE_TTL)
async def get_contact_info(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    contact_type: Optional[ContactType] = Query(None),
    primary_only: bool = Query(False),
    active_only: bool = Query(True),
    service: BaseService = Depends(get_contact_info_service)
) -> PaginatedResponse:
    pagination = PaginationParams(page=page, size=size)
    filter_conditions = {}
    
    if active_only:
        filter_conditions["isActive"] = True
    if contact_type:
        filter_conditions["type"] = contact_type.value
    if primary_only:
        filter_conditions["isPrimary"] = True
    
    return await service.get_all(
        pagination=pagination,
        filter_conditions=filter_conditions if filter_conditions else None
    )


@router.get("/{record_id}", response_model=ContactInfo)
# @cache(expire=settings.CACHE_TTL)
async def get_contact_info_item(
    record_id: str,
    service: BaseService = Depends(get_contact_info_service)
) -> ContactInfo:
    result = await service.get_by_id(record_id)
    if not result:
        raise HTTPException(status_code=404, detail="Contact info not found")
    return result


@router.patch("/{record_id}", response_model=ContactInfo)
async def update_contact_info(
    record_id: str,
    data: ContactInfoUpdate,
    service: BaseService = Depends(get_contact_info_service)
) -> ContactInfo:
    return await service.update(record_id, data)


@router.delete("/{record_id}", response_model=BaseResponse)
async def delete_contact_info(
    record_id: str,
    hard_delete: bool = Query(False),
    service: BaseService = Depends(get_contact_info_service)
) -> BaseResponse:
    if hard_delete:
        await service.delete(record_id)
        message = "Contact info deleted permanently"
    else:
        await service.update(record_id, ContactInfoUpdate(isActive=False))
        message = "Contact info deactivated"
    return BaseResponse(success=True, message=message)
