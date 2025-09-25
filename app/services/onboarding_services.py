"""
PostgreSQL services for onboarding flow management.
"""

import uuid
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.orm import selectinload

from app.services.postgres_base import PostgresBaseService
from app.database.postgres import get_db_session
from fastapi import Depends
from app.models.database import (
    OnboardingStep as OnboardingStepModel, 
    OnboardingStepProgress as OnboardingStepProgressModel, 
    OnboardingAnalytics as OnboardingAnalyticsModel,
    ServiceType, StepName, StepStatus, ConversionStatus, DeviceType
)
from app.models.schemas import (
    OnboardingStep as OnboardingStepSchema,
    OnboardingStepProgress as OnboardingStepProgressSchema,
    OnboardingAnalytics as OnboardingAnalyticsSchema,
    OnboardingStepCreate, OnboardingStepUpdate,
    OnboardingStepProgressCreate, OnboardingStepProgressUpdate,
    OnboardingAnalyticsCreate, OnboardingAnalyticsUpdate,
    StartOnboardingFlowRequest, SubmitStepDataRequest,
    ValidationResult, OnboardingFlowConfig, OnboardingFlowState
)
from app.core.exceptions import NotFoundError, ValidationException

logger = logging.getLogger(__name__)


class OnboardingStepsService(PostgresBaseService[OnboardingStepModel, OnboardingStepCreate, OnboardingStepUpdate, OnboardingStepSchema]):
    """Service for managing onboarding steps configuration."""

    def __init__(self, session: AsyncSession):
        super().__init__(
            model=OnboardingStepModel,
            response_schema=OnboardingStepSchema,
            session=session
        )

    async def get_steps_for_service_type(self, service_type: ServiceType) -> List[OnboardingStepSchema]:
        """Get all active steps for a specific service type, ordered by step_number."""
        try:
            query = (
                select(OnboardingStepModel)
                .where(
                    and_(
                        OnboardingStepModel.is_active == True,
                        or_(
                            OnboardingStepModel.service_types.contains([service_type.value]),
                            OnboardingStepModel.service_types.is_(None)
                        )
                    )
                )
                .order_by(OnboardingStepModel.step_number)
            )
            
            result = await self.session.execute(query)
            records = result.scalars().all()
            return [OnboardingStepSchema.from_orm(record) for record in records]
            
        except Exception as e:
            logger.error(f"Error getting steps for service type {service_type}: {e}")
            raise

    async def get_next_step(self, current_step_id: str, service_type: ServiceType) -> Optional[OnboardingStepSchema]:
        """Get the next step in the flow based on current step and service type."""
        try:
            # Get current step
            current_step = await self.get_by_id(current_step_id)
            if not current_step:
                return None

            # Get next step by step_number
            query = (
                select(OnboardingStepModel)
                .where(
                    and_(
                        OnboardingStepModel.step_number > current_step.step_number,
                        OnboardingStepModel.is_active == True,
                        or_(
                            OnboardingStepModel.service_types.contains([service_type.value]),
                            OnboardingStepModel.service_types.is_(None)
                        )
                    )
                )
                .order_by(OnboardingStepModel.step_number)
                .limit(1)
            )
            
            result = await self.session.execute(query)
            record = result.scalar_one_or_none()
            return OnboardingStepSchema.from_orm(record) if record else None
            
        except Exception as e:
            logger.error(f"Error getting next step for {current_step_id}: {e}")
            raise

    async def get_previous_step(self, current_step_id: str, service_type: ServiceType) -> Optional[OnboardingStepSchema]:
        """Get the previous step in the flow."""
        try:
            # Get current step
            current_step = await self.get_by_id(current_step_id)
            if not current_step:
                return None

            # Get previous step by step_number
            query = (
                select(OnboardingStepModel)
                .where(
                    and_(
                        OnboardingStepModel.step_number < current_step.step_number,
                        OnboardingStepModel.is_active == True,
                        or_(
                            OnboardingStepModel.service_types.contains([service_type.value]),
                            OnboardingStepModel.service_types.is_(None)
                        )
                    )
                )
                .order_by(desc(OnboardingStepModel.step_number))
                .limit(1)
            )
            
            result = await self.session.execute(query)
            record = result.scalar_one_or_none()
            return OnboardingStepSchema.from_orm(record) if record else None
            
        except Exception as e:
            logger.error(f"Error getting previous step for {current_step_id}: {e}")
            raise


class OnboardingProgressService(PostgresBaseService[OnboardingStepProgressModel, OnboardingStepProgressCreate, OnboardingStepProgressUpdate, OnboardingStepProgressSchema]):
    """Service for managing onboarding step progress."""

    def __init__(self, session: AsyncSession):
        super().__init__(
            model=OnboardingStepProgressModel,
            response_schema=OnboardingStepProgressSchema,
            session=session
        )

    async def get_session_progress(self, session_id: str) -> List[OnboardingStepProgressSchema]:
        """Get all progress records for a session."""
        try:
            query = (
                select(OnboardingStepProgressModel)
                .where(OnboardingStepProgressModel.submission_id == session_id)
                .order_by(OnboardingStepProgressModel.step_number)
            )
            
            result = await self.session.execute(query)
            records = result.scalars().all()
            return [OnboardingStepProgressSchema.from_orm(record) for record in records]
            
        except Exception as e:
            logger.error(f"Error getting session progress for {session_id}: {e}")
            raise

    async def get_step_progress(self, session_id: str, step_id: str) -> Optional[OnboardingStepProgressSchema]:
        """Get progress for a specific step in a session."""
        try:
            query = (
                select(OnboardingStepProgressModel)
                .where(
                    and_(
                        OnboardingStepProgressModel.submission_id == session_id,
                        OnboardingStepProgressModel.step_id == step_id
                    )
                )
            )
            
            result = await self.session.execute(query)
            record = result.scalar_one_or_none()
            return OnboardingStepProgressSchema.from_orm(record) if record else None
            
        except Exception as e:
            logger.error(f"Error getting step progress for {session_id}/{step_id}: {e}")
            raise

    async def update_step_status(self, session_id: str, step_id: str, status: StepStatus, **kwargs) -> OnboardingStepProgressSchema:
        """Update step status and additional fields."""
        try:
            progress = await self.get_step_progress(session_id, step_id)
            
            if not progress:
                raise NotFoundError(f"Step progress not found for session {session_id}, step {step_id}")

            # Update status and timestamp
            update_data = {"status": status, **kwargs}
            
            if status == StepStatus.IN_PROGRESS and not progress.started_at:
                update_data["started_at"] = datetime.utcnow()
            elif status == StepStatus.COMPLETED and not progress.completed_at:
                update_data["completed_at"] = datetime.utcnow()
            elif status == StepStatus.ERROR and not progress.exited_at:
                update_data["exited_at"] = datetime.utcnow()

            return await self.update(progress.id, OnboardingStepProgressUpdate(**update_data))
            
        except Exception as e:
            logger.error(f"Error updating step status for {session_id}/{step_id}: {e}")
            raise

    async def calculate_time_spent(self, session_id: str, step_id: str) -> int:
        """Calculate time spent on a step in seconds."""
        try:
            progress = await self.get_step_progress(session_id, step_id)
            
            if not progress or not progress.started_at:
                return 0

            end_time = progress.completed_at or progress.exited_at or datetime.utcnow()
            return int((end_time - progress.started_at).total_seconds())
            
        except Exception as e:
            logger.error(f"Error calculating time spent for {session_id}/{step_id}: {e}")
            return 0


class OnboardingAnalyticsService(PostgresBaseService[OnboardingAnalyticsModel, OnboardingAnalyticsCreate, OnboardingAnalyticsUpdate, OnboardingAnalyticsSchema]):
    """Service for managing onboarding analytics."""

    def __init__(self, session: AsyncSession):
        super().__init__(
            model=OnboardingAnalyticsModel,
            response_schema=OnboardingAnalyticsSchema,
            session=session
        )

    async def get_by_session_id(self, session_id: str) -> Optional[OnboardingAnalyticsSchema]:
        """Get analytics by session ID."""
        try:
            query = select(OnboardingAnalyticsModel).where(OnboardingAnalyticsModel.session_id == session_id)
            result = await self.session.execute(query)
            record = result.scalar_one_or_none()
            return OnboardingAnalyticsSchema.from_orm(record) if record else None
            
        except Exception as e:
            logger.error(f"Error getting analytics for session {session_id}: {e}")
            raise

    async def update_analytics_from_progress(self, session_id: str, progress_records: List[OnboardingStepProgressSchema]) -> OnboardingAnalyticsSchema:
        """Update analytics based on progress records."""
        try:
            analytics = await self.get_by_session_id(session_id)
            
            if not analytics:
                raise NotFoundError(f"Analytics not found for session {session_id}")

            # Calculate metrics
            completed_steps = len([p for p in progress_records if p.status == StepStatus.COMPLETED])
            skipped_steps = len([p for p in progress_records if p.status == StepStatus.SKIPPED])
            error_steps = len([p for p in progress_records if p.status == StepStatus.ERROR])
            
            total_time = sum(p.time_spent or 0 for p in progress_records)
            avg_time = total_time // max(completed_steps, 1) if completed_steps > 0 else 0
            
            completion_rate = (completed_steps * 100) // analytics.total_steps if analytics.total_steps > 0 else 0
            
            # Find fastest and slowest steps
            completed_progress = [p for p in progress_records if p.status == StepStatus.COMPLETED and p.time_spent]
            fastest_step = min(completed_progress, key=lambda x: x.time_spent).step_name.value if completed_progress else None
            slowest_step = max(completed_progress, key=lambda x: x.time_spent).step_name.value if completed_progress else None
            
            # Determine conversion status
            if completion_rate >= 100:
                conversion_status = ConversionStatus.COMPLETED
            elif any(p.status == StepStatus.ERROR for p in progress_records):
                conversion_status = ConversionStatus.ABANDONED
            else:
                conversion_status = ConversionStatus.IN_PROGRESS

            # Update analytics
            update_data = OnboardingAnalyticsUpdate(
                completed_steps=completed_steps,
                skipped_steps=skipped_steps,
                error_steps=error_steps,
                total_time_spent=total_time,
                average_step_time=avg_time,
                fastest_step=fastest_step,
                slowest_step=slowest_step,
                completion_rate=completion_rate,
                conversion_status=conversion_status,
                error_count=sum(p.attempt_count - 1 for p in progress_records),
                back_navigation_count=sum(len(p.navigation_history or []) for p in progress_records)
            )
            
            return await self.update(analytics.id, update_data)
            
        except Exception as e:
            logger.error(f"Error updating analytics for session {session_id}: {e}")
            raise

    async def get_summary_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get summary analytics for the last N days."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            query = (
                select(
                    func.count(OnboardingAnalyticsModel.id).label('total_sessions'),
                    func.avg(OnboardingAnalyticsModel.completion_rate).label('avg_completion_rate'),
                    func.avg(OnboardingAnalyticsModel.total_time_spent).label('avg_total_time'),
                    func.count().filter(OnboardingAnalyticsModel.conversion_status == ConversionStatus.COMPLETED).label('completed_sessions'),
                    func.count().filter(OnboardingAnalyticsModel.conversion_status == ConversionStatus.ABANDONED).label('abandoned_sessions')
                )
                .where(OnboardingAnalyticsModel.created_at >= cutoff_date)
            )
            
            result = await self.session.execute(query)
            row = result.first()
            
            return {
                'total_sessions': row.total_sessions or 0,
                'average_completion_rate': round(row.avg_completion_rate or 0, 2),
                'average_total_time': round(row.avg_total_time or 0, 2),
                'completed_sessions': row.completed_sessions or 0,
                'abandoned_sessions': row.abandoned_sessions or 0,
                'conversion_rate': round((row.completed_sessions or 0) / max(row.total_sessions or 1, 1) * 100, 2)
            }
            
        except Exception as e:
            logger.error(f"Error getting summary analytics: {e}")
            raise


class OnboardingFlowService:
    """Service for managing complete onboarding flows."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.steps_service = OnboardingStepsService(session)
        self.progress_service = OnboardingProgressService(session)
        self.analytics_service = OnboardingAnalyticsService(session)

    async def start_flow(self, request: StartOnboardingFlowRequest) -> Dict[str, Any]:
        """Start a new onboarding flow."""
        try:
            session_id = str(uuid.uuid4())
            
            # Get steps for service type
            steps = await self.steps_service.get_steps_for_service_type(request.service_type)
            
            if not steps:
                raise ValidationException(f"No steps configured for service type: {request.service_type}")

            # Create analytics record
            analytics_data = OnboardingAnalyticsCreate(
                session_id=session_id,
                total_steps=len(steps),
                user_agent=request.user_agent,
                device_type=request.device_type,
                screen_resolution=request.screen_resolution
            )
            analytics = await self.analytics_service.create(analytics_data)

            # Create progress records for all steps
            for step in steps:
                progress_data = OnboardingStepProgressCreate(
                    submission_id=session_id,
                    step_id=step.id,
                    step_number=step.step_number,
                    step_name=step.step_name,
                    status=StepStatus.PENDING if step.step_number > 1 else StepStatus.IN_PROGRESS,
                    user_agent=request.user_agent,
                    device_type=request.device_type,
                    started_at=datetime.utcnow() if step.step_number == 1 else None
                )
                await self.progress_service.create(progress_data)

            # Build flow config
            flow_config = OnboardingFlowConfig(
                steps=steps,
                service_type=request.service_type,
                total_steps=len(steps),
                current_step=1,
                progress=0,
                can_go_back=False,
                can_go_next=True,
                can_skip=steps[0].skip_conditions is not None if steps else False
            )

            return {
                'session_id': session_id,
                'flow_config': flow_config,
                'current_step': steps[0] if steps else None,
                'analytics_id': analytics.id
            }
            
        except Exception as e:
            logger.error(f"Error starting onboarding flow: {e}")
            raise

    async def submit_step_data(self, request: SubmitStepDataRequest) -> Dict[str, Any]:
        """Submit step data and progress to next step."""
        try:
            # Get current step progress
            progress = await self.progress_service.get_step_progress(request.session_id, request.step_id)
            
            if not progress:
                raise NotFoundError(f"Step progress not found for session {request.session_id}, step {request.step_id}")

            # Validate step data (basic validation for now)
            validation_result = ValidationResult(is_valid=True, errors=[], warnings=[])
            
            # Update progress
            time_spent = request.time_spent or await self.progress_service.calculate_time_spent(request.session_id, request.step_id)
            
            await self.progress_service.update_step_status(
                request.session_id,
                request.step_id,
                StepStatus.COMPLETED,
                step_data=request.step_data,
                user_input=request.step_data,
                time_spent=time_spent,
                completed_at=datetime.utcnow()
            )

            # Get current step and find next step
            current_step = await self.steps_service.get_by_id(request.step_id)
            next_step = await self.steps_service.get_next_step(request.step_id, ServiceType.LANDING_PAGE)  # TODO: get from session

            # Start next step if exists
            if next_step:
                await self.progress_service.update_step_status(
                    request.session_id,
                    next_step.id,
                    StepStatus.IN_PROGRESS,
                    started_at=datetime.utcnow()
                )

            # Update analytics
            all_progress = await self.progress_service.get_session_progress(request.session_id)
            await self.analytics_service.update_analytics_from_progress(request.session_id, all_progress)

            # Calculate progress percentage
            completed_count = len([p for p in all_progress if p.status == StepStatus.COMPLETED])
            progress_percentage = (completed_count * 100) // len(all_progress)

            return {
                'success': True,
                'validation_result': validation_result,
                'next_step': next_step,
                'progress_percentage': progress_percentage,
                'can_proceed': next_step is not None
            }
            
        except Exception as e:
            logger.error(f"Error submitting step data: {e}")
            raise

    async def get_flow_state(self, session_id: str) -> Optional[OnboardingFlowState]:
        """Get current flow state for a session."""
        try:
            # Get analytics and progress
            analytics = await self.analytics_service.get_by_session_id(session_id)
            if not analytics:
                return None

            progress_records = await self.progress_service.get_session_progress(session_id)
            
            # Find current step
            current_progress = next((p for p in progress_records if p.status == StepStatus.IN_PROGRESS), None)
            if not current_progress:
                current_progress = progress_records[-1] if progress_records else None

            # Build accumulated form data
            form_data = {}
            for progress in progress_records:
                if progress.step_data:
                    form_data.update(progress.step_data)

            return OnboardingFlowState(
                session_id=session_id,
                submission_id=analytics.submission_id,
                current_step=current_progress.step_number if current_progress else 1,
                current_step_name=current_progress.step_name if current_progress else StepName.SERVICE_SELECTION,
                step_history=[p.step_id for p in progress_records if p.status == StepStatus.COMPLETED],
                form_data=form_data,
                service_type=ServiceType.LANDING_PAGE,  # TODO: store in session
                is_complete=analytics.conversion_status == ConversionStatus.COMPLETED,
                started_at=analytics.created_at,
                last_active_at=analytics.updated_at
            )
            
        except Exception as e:
            logger.error(f"Error getting flow state for {session_id}: {e}")
            raise


# Dependency functions
def get_onboarding_steps_service(session: AsyncSession = Depends(get_db_session)) -> OnboardingStepsService:
    """Dependency to get onboarding steps service."""
    return OnboardingStepsService(session)


def get_onboarding_progress_service(session: AsyncSession = Depends(get_db_session)) -> OnboardingProgressService:
    """Dependency to get onboarding progress service."""
    return OnboardingProgressService(session)


def get_onboarding_analytics_service(session: AsyncSession = Depends(get_db_session)) -> OnboardingAnalyticsService:
    """Dependency to get onboarding analytics service."""
    return OnboardingAnalyticsService(session)


def get_onboarding_flow_service(session: AsyncSession = Depends(get_db_session)) -> OnboardingFlowService:
    """Dependency to get onboarding flow service."""
    return OnboardingFlowService(session)