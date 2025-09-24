"""
Features API endpoints.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_cache.decorator import cache

from app.database.xata import get_database, XataDB
from app.models.content import Feature, FeatureCreate, FeatureUpdate
from app.models.base import PaginationParams, PaginatedResponse, BaseResponse
from app.services.base import BaseService
from app.core.exceptions import NotFoundError
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


def get_features_service(db: XataDB = Depends(get_database)) -> BaseService:
    """Get features service instance."""
    return BaseService(
        db=db,
        table_name="features",
        model_class=Feature,
        create_model_class=FeatureCreate,
        update_model_class=FeatureUpdate
    )


@router.post(
    "/",
    response_model=Feature,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new feature"
)
async def create_feature(
    feature_data: FeatureCreate,
    service: BaseService = Depends(get_features_service)
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
@cache(expire=settings.CACHE_TTL)
async def get_features(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    active_only: bool = Query(True),
    service: BaseService = Depends(get_features_service)
) -> PaginatedResponse:
    """Get all features with pagination."""
    try:
        pagination = PaginationParams(page=page, size=size)
        filter_conditions = {"isActive": True} if active_only else None
        
        return await service.get_all(
            pagination=pagination,
            filter_conditions=filter_conditions
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
@cache(expire=settings.CACHE_TTL)
async def get_feature(
    record_id: str,
    service: BaseService = Depends(get_features_service)
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
    service: BaseService = Depends(get_features_service)
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
    service: BaseService = Depends(get_features_service)
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
            await service.update(record_id, FeatureUpdate(isActive=False))
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
