"""
Hero section API endpoints.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
# Caching temporarily disabled for deployment

from app.database.xata import get_database, XataDB
from app.models.content import HeroSection, HeroSectionCreate, HeroSectionUpdate
from app.models.base import PaginationParams, PaginatedResponse, BaseResponse
from app.services.base import BaseService
from app.core.exceptions import NotFoundError
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


def get_hero_section_service(db: XataDB = Depends(get_database)) -> BaseService:
    """Get hero section service instance."""
    return BaseService(
        db=db,
        table_name="hero_section",
        model_class=HeroSection,
        create_model_class=HeroSectionCreate,
        update_model_class=HeroSectionUpdate
    )


@router.post("/", response_model=HeroSection, status_code=status.HTTP_201_CREATED)
async def create_hero_section(
    data: HeroSectionCreate,
    service: BaseService = Depends(get_hero_section_service)
) -> HeroSection:
    return await service.create(data)


@router.get("/", response_model=PaginatedResponse)
# @cache(expire=settings.CACHE_TTL)
async def get_hero_sections(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    active_only: bool = Query(True),
    service: BaseService = Depends(get_hero_section_service)
) -> PaginatedResponse:
    pagination = PaginationParams(page=page, size=size)
    filter_conditions = {"isActive": True} if active_only else None
    return await service.get_all(pagination=pagination, filter_conditions=filter_conditions)


@router.get("/{record_id}", response_model=HeroSection)
# @cache(expire=settings.CACHE_TTL)
async def get_hero_section(
    record_id: str,
    service: BaseService = Depends(get_hero_section_service)
) -> HeroSection:
    result = await service.get_by_id(record_id)
    if not result:
        raise HTTPException(status_code=404, detail="Hero section not found")
    return result


@router.patch("/{record_id}", response_model=HeroSection)
async def update_hero_section(
    record_id: str,
    data: HeroSectionUpdate,
    service: BaseService = Depends(get_hero_section_service)
) -> HeroSection:
    return await service.update(record_id, data)


@router.delete("/{record_id}", response_model=BaseResponse)
async def delete_hero_section(
    record_id: str,
    hard_delete: bool = Query(False),
    service: BaseService = Depends(get_hero_section_service)
) -> BaseResponse:
    if hard_delete:
        await service.delete(record_id)
        message = "Hero section deleted permanently"
    else:
        await service.update(record_id, HeroSectionUpdate(isActive=False))
        message = "Hero section deactivated"
    return BaseResponse(success=True, message=message)
