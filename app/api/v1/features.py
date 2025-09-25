"""
Features API endpoints.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db_session
from app.models.schemas import Feature, FeatureCreate, FeatureUpdate, PaginationParams, PaginatedResponse, BaseResponse
from app.services.postgres_services import PostgresFeaturesService
from app.core.exceptions import NotFoundError
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


def get_features_service(session: AsyncSession = Depends(get_db_session)) -> PostgresFeaturesService:
    """Get features service instance."""
    return PostgresFeaturesService(session)


@router.post(
    "/",
    response_model=Feature,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new feature"
)
async def create_feature(
    feature_data: FeatureCreate,
    service: PostgresFeaturesService = Depends(get_features_service)
) -> Feature:
    """Create a new feature."""
    try:
        return await service.create(feature_data)
    except Exception as e:
        logger.error(f"Error creating feature: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create feature"
        )


@router.get(
    "/",
    response_model=PaginatedResponse,
    summary="Get all features"
)
# @cache(expire=settings.CACHE_TTL)
async def get_features(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    active_only: bool = Query(True),
    service: PostgresFeaturesService = Depends(get_features_service)
) -> PaginatedResponse:
    """Get all features with pagination."""
    try:
        pagination = PaginationParams(page=page, size=size)
        filters = {"is_active": True} if active_only else None
        
        return await service.get_all(
            pagination=pagination,
            filters=filters
        )
    except Exception as e:
        logger.error(f"Error getting features: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve features"
        )


@router.get(
    "/{record_id}",
    response_model=Feature,
    summary="Get feature by ID"
)
# @cache(expire=settings.CACHE_TTL)
async def get_feature(
    record_id: str,
    service: PostgresFeaturesService = Depends(get_features_service)
) -> Feature:
    """Get feature by ID."""
    try:
        feature = await service.get_by_id(record_id)
        if not feature:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feature with ID '{record_id}' not found"
            )
        return feature
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting feature {record_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve feature"
        )


@router.patch(
    "/{record_id}",
    response_model=Feature,
    summary="Update feature"
)
async def update_feature(
    record_id: str,
    feature_data: FeatureUpdate,
    service: PostgresFeaturesService = Depends(get_features_service)
) -> Feature:
    """Update feature."""
    try:
        return await service.update(record_id, feature_data)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail
        )
    except Exception as e:
        logger.error(f"Error updating feature {record_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update feature"
        )


@router.delete(
    "/{record_id}",
    response_model=BaseResponse,
    summary="Delete feature"
)
async def delete_feature(
    record_id: str,
    hard_delete: bool = Query(False, description="Perform hard delete"),
    service: PostgresFeaturesService = Depends(get_features_service)
) -> BaseResponse:
    """Delete feature."""
    try:
        if hard_delete:
            success = await service.delete(record_id)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Feature with ID '{record_id}' not found"
                )
            message = "Feature deleted permanently"
        else:
            await service.update(record_id, FeatureUpdate(is_active=False))
            message = "Feature deactivated"
        
        return BaseResponse(success=True, message=message)
    except HTTPException:
        raise
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail
        )
    except Exception as e:
        logger.error(f"Error deleting feature {record_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete feature"
        )
