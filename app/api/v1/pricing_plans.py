"""
Pricing plans API endpoints.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db_session
from app.models.schemas import (
    PricingPlan, 
    PricingPlanCreate, 
    PricingPlanUpdate, 
    PaginationParams, 
    PaginatedResponse, 
    BaseResponse
)
from app.models.database import PlanCategory
from app.services.postgres_pricing_plans import PostgresPricingPlansService
from app.core.exceptions import NotFoundError, ValidationException
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


def get_pricing_plans_service(session: AsyncSession = Depends(get_db_session)) -> PostgresPricingPlansService:
    """Get pricing plans service instance."""
    return PostgresPricingPlansService(session)


@router.post(
    "/",
    response_model=PricingPlan,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new pricing plan",
    description="Create a new pricing plan with unique planId"
)
async def create_pricing_plan(
    plan_data: PricingPlanCreate,
    service: PostgresPricingPlansService = Depends(get_pricing_plans_service)
) -> PricingPlan:
    """Create a new pricing plan."""
    try:
        return await service.create(plan_data)
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.detail
        )
    except Exception as e:
        logger.error(f"Error creating pricing plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create pricing plan"
        )


@router.get(
    "/",
    response_model=PaginatedResponse,
    summary="Get all pricing plans",
    description="Get paginated list of pricing plans with optional filtering"
)
# @cache(expire=settings.CACHE_TTL)
async def get_pricing_plans(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    category: Optional[PlanCategory] = Query(None, description="Filter by category"),
    active_only: bool = Query(True, description="Filter active plans only"),
    service: PostgresPricingPlansService = Depends(get_pricing_plans_service)
) -> PaginatedResponse:
    """Get all pricing plans with pagination and filtering."""
    try:
        pagination = PaginationParams(page=page, size=size)
        
        # Build filter conditions
        filter_conditions = {}
        if category:
            filter_conditions["category"] = category.value
        if active_only:
            filter_conditions["is_active"] = True
        
        return await service.get_all(
            pagination=pagination,
            filters=filter_conditions if filter_conditions else None
        )
        
    except Exception as e:
        logger.error(f"Error getting pricing plans: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve pricing plans"
        )


@router.get(
    "/popular",
    response_model=List[PricingPlan],
    summary="Get popular pricing plans",
    description="Get list of popular pricing plans"
)
# @cache(expire=settings.CACHE_TTL)
async def get_popular_pricing_plans(
    limit: int = Query(3, ge=1, le=10, description="Maximum number of popular plans"),
    service: PostgresPricingPlansService = Depends(get_pricing_plans_service)
) -> List[PricingPlan]:
    """Get popular pricing plans."""
    try:
        return await service.get_popular_plans(limit=limit)
    except Exception as e:
        logger.error(f"Error getting popular pricing plans: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve popular pricing plans"
        )


@router.get(
    "/category/{category}",
    response_model=List[PricingPlan],
    summary="Get pricing plans by category",
    description="Get all pricing plans for a specific category"
)
# @cache(expire=settings.CACHE_TTL)
async def get_pricing_plans_by_category(
    category: PlanCategory,
    service: PostgresPricingPlansService = Depends(get_pricing_plans_service)
) -> List[PricingPlan]:
    """Get pricing plans by category."""
    try:
        return await service.get_by_category(category)
    except Exception as e:
        logger.error(f"Error getting pricing plans by category {category}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve pricing plans for category {category}"
        )


@router.get(
    "/plan-id/{plan_id}",
    response_model=PricingPlan,
    summary="Get pricing plan by planId",
    description="Get a specific pricing plan by its planId"
)
# @cache(expire=settings.CACHE_TTL)
async def get_pricing_plan_by_plan_id(
    plan_id: str,
    service: PostgresPricingPlansService = Depends(get_pricing_plans_service)
) -> PricingPlan:
    """Get pricing plan by planId."""
    try:
        plan = await service.get_by_plan_id(plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pricing plan with planId '{plan_id}' not found"
            )
        return plan
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting pricing plan by planId {plan_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve pricing plan"
        )


@router.get(
    "/{id}",
    response_model=PricingPlan,
    summary="Get pricing plan by ID",
    description="Get a specific pricing plan by its database ID"
)
# @cache(expire=settings.CACHE_TTL)
async def get_pricing_plan(
    id: str,
    service: PostgresPricingPlansService = Depends(get_pricing_plans_service)
) -> PricingPlan:
    """Get pricing plan by ID."""
    try:
        plan = await service.get_by_id(id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pricing plan with ID '{id}' not found"
            )
        return plan
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting pricing plan {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve pricing plan"
        )


@router.patch(
    "/{id}",
    response_model=PricingPlan,
    summary="Update pricing plan",
    description="Update an existing pricing plan"
)
async def update_pricing_plan(
    id: str,
    plan_data: PricingPlanUpdate,
    service: PostgresPricingPlansService = Depends(get_pricing_plans_service)
) -> PricingPlan:
    """Update pricing plan."""
    try:
        return await service.update(id, plan_data)
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
        logger.error(f"Error updating pricing plan {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update pricing plan"
        )


@router.patch(
    "/{id}/popular",
    response_model=PricingPlan,
    summary="Set pricing plan popular status",
    description="Set whether a pricing plan is marked as popular"
)
async def set_pricing_plan_popular_status(
    id: str,
    popular: bool,
    service: PostgresPricingPlansService = Depends(get_pricing_plans_service)
) -> PricingPlan:
    """Set pricing plan popular status."""
    try:
        return await service.set_popular_status(id, popular)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail
        )
    except Exception as e:
        logger.error(f"Error setting popular status for pricing plan {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update pricing plan popular status"
        )


@router.post(
    "/reorder",
    response_model=List[PricingPlan],
    summary="Reorder pricing plans",
    description="Update display order for multiple pricing plans"
)
async def reorder_pricing_plans(
    plan_orders: List[dict],
    service: PostgresPricingPlansService = Depends(get_pricing_plans_service)
) -> List[PricingPlan]:
    """
    Reorder pricing plans.
    
    Request body should be a list of objects with 'id' and 'displayOrder' keys:
    [
        {"id": "plan_id_1", "displayOrder": 1},
        {"id": "plan_id_2", "displayOrder": 2}
    ]
    """
    try:
        return await service.reorder_plans(plan_orders)
    except Exception as e:
        logger.error(f"Error reordering pricing plans: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reorder pricing plans"
        )


@router.delete(
    "/{id}",
    response_model=BaseResponse,
    summary="Delete pricing plan",
    description="Delete a pricing plan (soft delete by setting is_active to false)"
)
async def delete_pricing_plan(
    id: str,
    hard_delete: bool = Query(False, description="Perform hard delete instead of soft delete"),
    service: PostgresPricingPlansService = Depends(get_pricing_plans_service)
) -> BaseResponse:
    """Delete pricing plan."""
    try:
        if hard_delete:
            # Hard delete
            success = await service.delete(id)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Pricing plan with ID '{id}' not found"
                )
            message = "Pricing plan deleted permanently"
        else:
            # Soft delete
            await service.update(id, PricingPlanUpdate(is_active=False))
            message = "Pricing plan deactivated"
        
        return BaseResponse(
            success=True,
            message=message
        )
        
    except HTTPException:
        raise
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail
        )
    except Exception as e:
        logger.error(f"Error deleting pricing plan {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete pricing plan"
        )


@router.get(
    "/search/{query}",
    response_model=PaginatedResponse,
    summary="Search pricing plans",
    description="Full-text search in pricing plans"
)
async def search_pricing_plans(
    query: str,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    category: Optional[PlanCategory] = Query(None, description="Filter by category"),
    service: PostgresPricingPlansService = Depends(get_pricing_plans_service)
) -> PaginatedResponse:
    """Search pricing plans with full-text search."""
    try:
        pagination = PaginationParams(page=page, size=size)
        
        # Build filter conditions
        filter_conditions = {"is_active": True}
        if category:
            filter_conditions["category"] = category.value
        
        # Search in relevant fields
        search_fields = ["name", "description", "plan_id"]
        
        return await service.search(
            query=query,
            pagination=pagination,
            search_fields=search_fields,
            filters=filter_conditions
        )
        
    except Exception as e:
        logger.error(f"Error searching pricing plans: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search pricing plans"
        )
