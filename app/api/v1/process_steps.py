"""
Process steps API endpoints.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
# Caching temporarily disabled for deployment

from app.database.xata import get_database, XataDB
from app.models.content import ProcessStep, ProcessStepCreate, ProcessStepUpdate
from app.models.base import PaginationParams, PaginatedResponse, BaseResponse
from app.services.base import BaseService
from app.core.exceptions import NotFoundError
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


def get_process_steps_service(db: XataDB = Depends(get_database)) -> BaseService:
    """Get process steps service instance."""
    return BaseService(
        db=db,
        table_name="process_steps",
        model_class=ProcessStep,
        create_model_class=ProcessStepCreate,
        update_model_class=ProcessStepUpdate
    )


@router.post(
    "/",
    response_model=ProcessStep,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new process step"
)
async def create_process_step(
    step_data: ProcessStepCreate,
    service: BaseService = Depends(get_process_steps_service)
) -> ProcessStep:
    """Create a new process step."""
    try:
        return await service.create(step_data)
    except Exception as e:
        logger.error(f"Error creating process step: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create process step"
        )


@router.get(
    "/",
    response_model=PaginatedResponse,
    summary="Get all process steps"
)
# @cache(expire=settings.CACHE_TTL)
async def get_process_steps(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    active_only: bool = Query(True),
    service: BaseService = Depends(get_process_steps_service)
) -> PaginatedResponse:
    """Get all process steps with pagination."""
    try:
        pagination = PaginationParams(page=page, size=size)
        filter_conditions = {"isActive": True} if active_only else None
        
        return await service.get_all(
            pagination=pagination,
            filter_conditions=filter_conditions,
            sort_by="stepNumber"  # Sort by step number instead of displayOrder
        )
    except Exception as e:
        logger.error(f"Error getting process steps: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve process steps"
        )


@router.get(
    "/{record_id}",
    response_model=ProcessStep,
    summary="Get process step by ID"
)
# @cache(expire=settings.CACHE_TTL)
async def get_process_step(
    record_id: str,
    service: BaseService = Depends(get_process_steps_service)
) -> ProcessStep:
    """Get process step by ID."""
    try:
        step = await service.get_by_id(record_id)
        if not step:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Process step with ID '{record_id}' not found"
            )
        return step
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting process step {record_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve process step"
        )


@router.patch(
    "/{record_id}",
    response_model=ProcessStep,
    summary="Update process step"
)
async def update_process_step(
    record_id: str,
    step_data: ProcessStepUpdate,
    service: BaseService = Depends(get_process_steps_service)
) -> ProcessStep:
    """Update process step."""
    try:
        return await service.update(record_id, step_data)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail
        )
    except Exception as e:
        logger.error(f"Error updating process step {record_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update process step"
        )


@router.delete(
    "/{record_id}",
    response_model=BaseResponse,
    summary="Delete process step"
)
async def delete_process_step(
    record_id: str,
    hard_delete: bool = Query(False, description="Perform hard delete"),
    service: BaseService = Depends(get_process_steps_service)
) -> BaseResponse:
    """Delete process step."""
    try:
        if hard_delete:
            success = await service.delete(record_id)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Process step with ID '{record_id}' not found"
                )
            message = "Process step deleted permanently"
        else:
            await service.update(record_id, ProcessStepUpdate(isActive=False))
            message = "Process step deactivated"
        
        return BaseResponse(success=True, message=message)
    except HTTPException:
        raise
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail
        )
    except Exception as e:
        logger.error(f"Error deleting process step {record_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete process step"
        )
