"""
API endpoints for onboarding flow management.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db_session
from app.services.onboarding_services import (
    get_onboarding_steps_service, get_onboarding_progress_service,
    get_onboarding_analytics_service, get_onboarding_flow_service,
    OnboardingStepsService, OnboardingProgressService,
    OnboardingAnalyticsService, OnboardingFlowService
)
from app.models.schemas import (
    OnboardingStep, OnboardingStepCreate, OnboardingStepUpdate,
    OnboardingStepProgress, OnboardingStepProgressCreate, OnboardingStepProgressUpdate,
    OnboardingAnalytics, OnboardingAnalyticsCreate, OnboardingAnalyticsUpdate,
    StartOnboardingFlowRequest, StartOnboardingFlowResponse,
    SubmitStepDataRequest, SubmitStepDataResponse,
    OnboardingFlowState, BaseResponse, PaginatedResponse, PaginationParams,
    ServiceType, StepStatus, ConversionStatus
)
from app.core.exceptions import NotFoundError, ValidationException

logger = logging.getLogger(__name__)

router = APIRouter()


# Onboarding Steps Management
@router.get(
    "/steps",
    response_model=List[OnboardingStep],
    summary="Get all onboarding steps",
    description="Get all onboarding steps with optional filtering by service type"
)
async def get_onboarding_steps(
    service_type: Optional[ServiceType] = Query(None, description="Filter by service type"),
    service: OnboardingStepsService = Depends(get_onboarding_steps_service)
) -> List[OnboardingStep]:
    """Get all onboarding steps."""
    try:
        if service_type:
            return await service.get_steps_for_service_type(service_type)
        else:
            filters = {"is_active": True}
            pagination = PaginationParams(page=1, size=100)  # Get all steps
            result = await service.get_all(pagination=pagination, filters=filters, order_by="step_number")
            return result.items
    except Exception as e:
        logger.error(f"Error getting onboarding steps: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve onboarding steps"
        )


@router.get(
    "/steps/{step_id}",
    response_model=OnboardingStep,
    summary="Get onboarding step by ID",
    description="Get a specific onboarding step by its ID"
)
async def get_onboarding_step(
    step_id: str,
    service: OnboardingStepsService = Depends(get_onboarding_steps_service)
) -> OnboardingStep:
    """Get onboarding step by ID."""
    try:
        step = await service.get_by_id(step_id)
        if not step:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Onboarding step with ID '{step_id}' not found"
            )
        return step
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting onboarding step {step_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve onboarding step"
        )


@router.post(
    "/steps",
    response_model=OnboardingStep,
    status_code=status.HTTP_201_CREATED,
    summary="Create onboarding step",
    description="Create a new onboarding step"
)
async def create_onboarding_step(
    step_data: OnboardingStepCreate,
    service: OnboardingStepsService = Depends(get_onboarding_steps_service)
) -> OnboardingStep:
    """Create onboarding step."""
    try:
        return await service.create(step_data)
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.detail
        )
    except Exception as e:
        logger.error(f"Error creating onboarding step: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create onboarding step"
        )


@router.patch(
    "/steps/{step_id}",
    response_model=OnboardingStep,
    summary="Update onboarding step",
    description="Update an existing onboarding step"
)
async def update_onboarding_step(
    step_id: str,
    step_data: OnboardingStepUpdate,
    service: OnboardingStepsService = Depends(get_onboarding_steps_service)
) -> OnboardingStep:
    """Update onboarding step."""
    try:
        return await service.update(step_id, step_data)
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
        logger.error(f"Error updating onboarding step {step_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update onboarding step"
        )


@router.delete(
    "/steps/{step_id}",
    response_model=BaseResponse,
    summary="Delete onboarding step",
    description="Delete an onboarding step (soft delete by setting is_active to false)"
)
async def delete_onboarding_step(
    step_id: str,
    hard_delete: bool = Query(False, description="Perform hard delete instead of soft delete"),
    service: OnboardingStepsService = Depends(get_onboarding_steps_service)
) -> BaseResponse:
    """Delete onboarding step."""
    try:
        if hard_delete:
            success = await service.delete(step_id)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Onboarding step with ID '{step_id}' not found"
                )
            message = "Onboarding step deleted permanently"
        else:
            await service.update(step_id, OnboardingStepUpdate(is_active=False))
            message = "Onboarding step deactivated"
        
        return BaseResponse(success=True, message=message)
        
    except HTTPException:
        raise
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail
        )
    except Exception as e:
        logger.error(f"Error deleting onboarding step {step_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete onboarding step"
        )


# Onboarding Flow Management
@router.post(
    "/flow/start",
    response_model=StartOnboardingFlowResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start onboarding flow",
    description="Start a new onboarding flow for a specific service type"
)
async def start_onboarding_flow(
    flow_request: StartOnboardingFlowRequest,
    flow_service: OnboardingFlowService = Depends(get_onboarding_flow_service)
) -> StartOnboardingFlowResponse:
    """Start new onboarding flow."""
    try:
        result = await flow_service.start_flow(flow_request)
        return StartOnboardingFlowResponse(**result)
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.detail
        )
    except Exception as e:
        logger.error(f"Error starting onboarding flow: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start onboarding flow"
        )


@router.post(
    "/flow/submit",
    response_model=SubmitStepDataResponse,
    summary="Submit step data",
    description="Submit data for a specific step and progress to next step"
)
async def submit_step_data(
    submit_request: SubmitStepDataRequest,
    flow_service: OnboardingFlowService = Depends(get_onboarding_flow_service)
) -> SubmitStepDataResponse:
    """Submit step data."""
    try:
        result = await flow_service.submit_step_data(submit_request)
        return SubmitStepDataResponse(**result)
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
        logger.error(f"Error submitting step data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit step data"
        )


@router.get(
    "/flow/{session_id}",
    response_model=OnboardingFlowState,
    summary="Get flow state",
    description="Get current flow state for a session"
)
async def get_flow_state(
    session_id: str,
    flow_service: OnboardingFlowService = Depends(get_onboarding_flow_service)
) -> OnboardingFlowState:
    """Get flow state."""
    try:
        state = await flow_service.get_flow_state(session_id)
        if not state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Flow state not found for session '{session_id}'"
            )
        return state
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting flow state for {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve flow state"
        )


@router.post(
    "/flow/{session_id}/back",
    response_model=BaseResponse,
    summary="Go back to previous step",
    description="Navigate back to the previous step in the flow"
)
async def go_back_step(
    session_id: str,
    flow_service: OnboardingFlowService = Depends(get_onboarding_flow_service)
) -> BaseResponse:
    """Go back to previous step."""
    try:
        # TODO: Implement back navigation logic
        return BaseResponse(
            success=True,
            message="Navigated back to previous step"
        )
    except Exception as e:
        logger.error(f"Error going back in flow {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to navigate back"
        )


@router.post(
    "/flow/{session_id}/skip",
    response_model=BaseResponse,
    summary="Skip current step",
    description="Skip the current step in the flow"
)
async def skip_step(
    session_id: str,
    step_id: str = Query(..., description="Step ID to skip"),
    flow_service: OnboardingFlowService = Depends(get_onboarding_flow_service)
) -> BaseResponse:
    """Skip current step."""
    try:
        # TODO: Implement skip logic
        return BaseResponse(
            success=True,
            message="Step skipped successfully"
        )
    except Exception as e:
        logger.error(f"Error skipping step in flow {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to skip step"
        )


# Progress Management
@router.get(
    "/progress/{session_id}",
    response_model=List[OnboardingStepProgress],
    summary="Get session progress",
    description="Get all progress records for a session"
)
async def get_session_progress(
    session_id: str,
    service: OnboardingProgressService = Depends(get_onboarding_progress_service)
) -> List[OnboardingStepProgress]:
    """Get session progress."""
    try:
        return await service.get_session_progress(session_id)
    except Exception as e:
        logger.error(f"Error getting session progress for {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve session progress"
        )


@router.get(
    "/progress/{session_id}/{step_id}",
    response_model=OnboardingStepProgress,
    summary="Get step progress",
    description="Get progress for a specific step in a session"
)
async def get_step_progress(
    session_id: str,
    step_id: str,
    service: OnboardingProgressService = Depends(get_onboarding_progress_service)
) -> OnboardingStepProgress:
    """Get step progress."""
    try:
        progress = await service.get_step_progress(session_id, step_id)
        if not progress:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Progress not found for session '{session_id}', step '{step_id}'"
            )
        return progress
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting step progress for {session_id}/{step_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve step progress"
        )


# Analytics
@router.get(
    "/analytics/{session_id}",
    response_model=OnboardingAnalytics,
    summary="Get session analytics",
    description="Get analytics data for a specific session"
)
async def get_session_analytics(
    session_id: str,
    service: OnboardingAnalyticsService = Depends(get_onboarding_analytics_service)
) -> OnboardingAnalytics:
    """Get session analytics."""
    try:
        analytics = await service.get_by_session_id(session_id)
        if not analytics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analytics not found for session '{session_id}'"
            )
        return analytics
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analytics for {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analytics"
        )


@router.get(
    "/analytics/summary",
    summary="Get summary analytics",
    description="Get aggregated analytics for the last N days"
)
async def get_summary_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days to include"),
    service: OnboardingAnalyticsService = Depends(get_onboarding_analytics_service)
):
    """Get summary analytics."""
    try:
        return await service.get_summary_analytics(days)
    except Exception as e:
        logger.error(f"Error getting summary analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve summary analytics"
        )


@router.get(
    "/analytics/performance",
    summary="Get performance metrics",
    description="Get performance metrics for onboarding flows"
)
async def get_performance_metrics(
    service: OnboardingAnalyticsService = Depends(get_onboarding_analytics_service)
):
    """Get performance metrics."""
    try:
        # TODO: Implement performance metrics calculation
        return {
            "message": "Performance metrics endpoint - to be implemented",
            "metrics": {}
        }
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve performance metrics"
        )
