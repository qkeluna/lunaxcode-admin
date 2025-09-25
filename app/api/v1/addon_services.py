"""
Addon services API endpoints.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db_session
from app.models.schemas import AddonService, AddonServiceCreate, AddonServiceUpdate, PaginationParams, PaginatedResponse, BaseResponse
from app.models.database import ServiceCategory
from app.services.postgres_services import PostgresAddonServicesService
from app.core.exceptions import NotFoundError, ValidationException
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


def get_service(session: AsyncSession = Depends(get_db_session)) -> PostgresAddonServicesService:
    """Get service instance."""
    return PostgresAddonServicesService(session)


@router.post(
    "/",
    response_model=AddonService,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new addon service"
)
async def create_addon_service(
    service_data: AddonServiceCreate,
    service: PostgresAddonServicesService = Depends(get_service)
) -> AddonService:
    """Create a new addon service."""
    try:
        return await service.create(service_data)
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.detail
        )
    except Exception as e:
        logger.error(f"Error creating addon service: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create addon service"
        )


@router.get(
    "/",
    response_model=PaginatedResponse,
    summary="Get all addon services"
)
async def get_addon_services(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    category: Optional[ServiceCategory] = Query(None, description="Filter by category"),
    active_only: bool = Query(True),
    service: PostgresAddonServicesService = Depends(get_service)
) -> PaginatedResponse:
    """Get all addon services with pagination."""
    try:
        pagination = PaginationParams(page=page, size=size)
        filters = {}
        if category:
            filters["category"] = category
        if active_only:
            filters["is_active"] = True
        
        return await service.get_all(
            pagination=pagination,
            filters=filters or None
        )
    except Exception as e:
        logger.error(f"Error getting addon services: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve addon services"
        )


@router.get(
    "/popular",
    response_model=List[AddonService],
    summary="Get popular addon services"
)
async def get_popular_addon_services(
    limit: int = Query(5, ge=1, le=10, description="Maximum number of popular services"),
    service: PostgresAddonServicesService = Depends(get_service)
) -> List[AddonService]:
    """Get popular addon services."""
    try:
        return await service.get_popular_services(limit=limit)
    except Exception as e:
        logger.error(f"Error getting popular addon services: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve popular addon services"
        )


@router.get(
    "/category/{category}",
    response_model=List[AddonService],
    summary="Get addon services by category"
)
async def get_addon_services_by_category(
    category: ServiceCategory,
    service: PostgresAddonServicesService = Depends(get_service)
) -> List[AddonService]:
    """Get addon services by category."""
    try:
        return await service.get_by_category(category)
    except Exception as e:
        logger.error(f"Error getting addon services by category {category}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve addon services for category {category}"
        )


@router.get(
    "/service-id/{service_id}",
    response_model=AddonService,
    summary="Get addon service by service ID"
)
async def get_addon_service_by_service_id(
    service_id: str,
    service: PostgresAddonServicesService = Depends(get_service)
) -> AddonService:
    """Get addon service by service ID."""
    try:
        addon_service = await service.get_by_service_id(service_id)
        if not addon_service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Addon service with service ID '{service_id}' not found"
            )
        return addon_service
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting addon service by service ID {service_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve addon service"
        )


@router.get(
    "/{record_id}",
    response_model=AddonService,
    summary="Get addon service by ID"
)
async def get_addon_service(
    record_id: str,
    service: PostgresAddonServicesService = Depends(get_service)
) -> AddonService:
    """Get addon service by ID."""
    try:
        addon_service = await service.get_by_id(record_id)
        if not addon_service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Addon service with ID '{record_id}' not found"
            )
        return addon_service
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting addon service {record_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve addon service"
        )


@router.patch(
    "/{record_id}",
    response_model=AddonService,
    summary="Update addon service"
)
async def update_addon_service(
    record_id: str,
    service_data: AddonServiceUpdate,
    service: PostgresAddonServicesService = Depends(get_service)
) -> AddonService:
    """Update addon service."""
    try:
        return await service.update(record_id, service_data)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail
        )
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.detail
        )
    except Exception as e:
        logger.error(f"Error updating addon service {record_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update addon service"
        )


@router.delete(
    "/{record_id}",
    response_model=BaseResponse,
    summary="Delete addon service"
)
async def delete_addon_service(
    record_id: str,
    hard_delete: bool = Query(False, description="Perform hard delete"),
    service: PostgresAddonServicesService = Depends(get_service)
) -> BaseResponse:
    """Delete addon service."""
    try:
        if hard_delete:
            success = await service.delete(record_id)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Addon service with ID '{record_id}' not found"
                )
            message = "Addon service deleted permanently"
        else:
            await service.update(record_id, AddonServiceUpdate(is_active=False))
            message = "Addon service deactivated"
        
        return BaseResponse(success=True, message=message)
    except HTTPException:
        raise
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail
        )
    except Exception as e:
        logger.error(f"Error deleting addon service {record_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete addon service"
        )