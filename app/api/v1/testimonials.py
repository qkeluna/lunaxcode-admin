"""
Testimonials API endpoints.
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_cache.decorator import cache

from app.database.xata import get_database, XataDB
from app.models.content import Testimonial, TestimonialCreate, TestimonialUpdate, ProjectType
from app.models.base import PaginationParams, PaginatedResponse, BaseResponse
from app.services.base import BaseService
from app.core.exceptions import NotFoundError
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


def get_testimonials_service(db: XataDB = Depends(get_database)) -> BaseService:
    """Get testimonials service instance."""
    return BaseService(
        db=db,
        table_name="testimonials",
        model_class=Testimonial,
        create_model_class=TestimonialCreate,
        update_model_class=TestimonialUpdate
    )


@router.post("/", response_model=Testimonial, status_code=status.HTTP_201_CREATED)
async def create_testimonial(
    data: TestimonialCreate,
    service: BaseService = Depends(get_testimonials_service)
) -> Testimonial:
    return await service.create(data)


@router.get("/", response_model=PaginatedResponse)
@cache(expire=settings.CACHE_TTL)
async def get_testimonials(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    project_type: Optional[ProjectType] = Query(None),
    active_only: bool = Query(True),
    service: BaseService = Depends(get_testimonials_service)
) -> PaginatedResponse:
    pagination = PaginationParams(page=page, size=size)
    filter_conditions = {}
    
    if active_only:
        filter_conditions["isActive"] = True
    if project_type:
        filter_conditions["projectType"] = project_type.value
    
    return await service.get_all(
        pagination=pagination, 
        filter_conditions=filter_conditions if filter_conditions else None
    )


@router.get("/{record_id}", response_model=Testimonial)
@cache(expire=settings.CACHE_TTL)
async def get_testimonial(
    record_id: str,
    service: BaseService = Depends(get_testimonials_service)
) -> Testimonial:
    result = await service.get_by_id(record_id)
    if not result:
        raise HTTPException(status_code=404, detail="Testimonial not found")
    return result


@router.patch("/{record_id}", response_model=Testimonial)
async def update_testimonial(
    record_id: str,
    data: TestimonialUpdate,
    service: BaseService = Depends(get_testimonials_service)
) -> Testimonial:
    return await service.update(record_id, data)


@router.delete("/{record_id}", response_model=BaseResponse)
async def delete_testimonial(
    record_id: str,
    hard_delete: bool = Query(False),
    service: BaseService = Depends(get_testimonials_service)
) -> BaseResponse:
    if hard_delete:
        await service.delete(record_id)
        message = "Testimonial deleted permanently"
    else:
        await service.update(record_id, TestimonialUpdate(isActive=False))
        message = "Testimonial deactivated"
    return BaseResponse(success=True, message=message)
