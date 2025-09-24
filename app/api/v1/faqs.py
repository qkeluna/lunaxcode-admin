"""
FAQs API endpoints.
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
# Caching temporarily disabled for deployment

from app.database.xata import get_database, XataDB
from app.models.content import FAQ, FAQCreate, FAQUpdate, FAQCategory
from app.models.base import PaginationParams, PaginatedResponse, BaseResponse
from app.services.base import BaseService
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


def get_faqs_service(db: XataDB = Depends(get_database)) -> BaseService:
    return BaseService(
        db=db,
        table_name="faqs",
        model_class=FAQ,
        create_model_class=FAQCreate,
        update_model_class=FAQUpdate
    )


@router.post("/", response_model=FAQ, status_code=status.HTTP_201_CREATED)
async def create_faq(
    data: FAQCreate,
    service: BaseService = Depends(get_faqs_service)
) -> FAQ:
    return await service.create(data)


@router.get("/", response_model=PaginatedResponse)
# @cache(expire=settings.CACHE_TTL)
async def get_faqs(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    category: Optional[FAQCategory] = Query(None),
    active_only: bool = Query(True),
    service: BaseService = Depends(get_faqs_service)
) -> PaginatedResponse:
    pagination = PaginationParams(page=page, size=size)
    filter_conditions = {}
    
    if active_only:
        filter_conditions["isActive"] = True
    if category:
        filter_conditions["category"] = category.value
    
    return await service.get_all(
        pagination=pagination,
        filter_conditions=filter_conditions if filter_conditions else None
    )


@router.get("/{record_id}", response_model=FAQ)
# @cache(expire=settings.CACHE_TTL)
async def get_faq(
    record_id: str,
    service: BaseService = Depends(get_faqs_service)
) -> FAQ:
    result = await service.get_by_id(record_id)
    if not result:
        raise HTTPException(status_code=404, detail="FAQ not found")
    return result


@router.patch("/{record_id}", response_model=FAQ)
async def update_faq(
    record_id: str,
    data: FAQUpdate,
    service: BaseService = Depends(get_faqs_service)
) -> FAQ:
    return await service.update(record_id, data)


@router.delete("/{record_id}", response_model=BaseResponse)
async def delete_faq(
    record_id: str,
    hard_delete: bool = Query(False),
    service: BaseService = Depends(get_faqs_service)
) -> BaseResponse:
    if hard_delete:
        await service.delete(record_id)
        message = "FAQ deleted permanently"
    else:
        await service.update(record_id, FAQUpdate(isActive=False))
        message = "FAQ deactivated"
    return BaseResponse(success=True, message=message)
