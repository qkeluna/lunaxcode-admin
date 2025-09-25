"""
Pricing plans service for PostgreSQL operations.
"""

import logging
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import PricingPlan as PricingPlanModel, PlanCategory
from app.models.schemas import (
    PricingPlan, PricingPlanCreate, PricingPlanUpdate, PaginationParams, PaginatedResponse
)
from app.services.postgres_base import PostgresBaseService
from app.core.exceptions import ValidationException

logger = logging.getLogger(__name__)


class PostgresPricingPlansService(PostgresBaseService[PricingPlanModel, PricingPlanCreate, PricingPlanUpdate, PricingPlan]):
    """Service for managing pricing plans with PostgreSQL."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(
            model=PricingPlanModel,
            response_schema=PricingPlan,
            session=session
        )
    
    async def create(self, obj_in: PricingPlanCreate) -> PricingPlan:
        """Create a new pricing plan with validation."""
        # Validate plan_id uniqueness
        await self._validate_plan_id_unique(obj_in.plan_id)
        
        return await super().create(obj_in)
    
    async def update(self, id: str, obj_in: PricingPlanUpdate) -> PricingPlan:
        """Update pricing plan with validation."""
        # If plan_id is being updated, validate uniqueness
        if obj_in.plan_id is not None:
            existing_plan = await self.get_by_plan_id(obj_in.plan_id)
            if existing_plan and existing_plan.id != id:
                raise ValidationException(
                    f"Plan ID '{obj_in.plan_id}' already exists",
                    field="plan_id"
                )
        
        return await super().update(id, obj_in)
    
    async def get_by_plan_id(self, plan_id: str) -> Optional[PricingPlan]:
        """Get pricing plan by plan_id."""
        return await self.get_by_field("plan_id", plan_id)
    
    async def get_by_category(self, category: PlanCategory) -> List[PricingPlan]:
        """Get pricing plans by category."""
        filters = {"category": category, "is_active": True}
        result = await self.get_all(
            pagination=PaginationParams(page=1, size=100),
            filters=filters,
            order_by="display_order"
        )
        return result.items
    
    async def get_popular_plans(self, limit: int = 3) -> List[PricingPlan]:
        """Get popular pricing plans."""
        filters = {"popular": True, "is_active": True}
        result = await self.get_all(
            pagination=PaginationParams(page=1, size=limit),
            filters=filters,
            order_by="display_order"
        )
        return result.items
    
    async def set_popular_status(self, id: str, popular: bool) -> PricingPlan:
        """Set popular status for a pricing plan."""
        update_data = PricingPlanUpdate(popular=popular)
        return await self.update(id, update_data)
    
    async def reorder_plans(self, plan_orders: List[dict]) -> List[PricingPlan]:
        """
        Reorder pricing plans.
        
        Args:
            plan_orders: List of dicts with 'id' and 'display_order' keys
        
        Returns:
            List of updated pricing plans
        """
        updates = []
        for plan_order in plan_orders:
            plan_id = plan_order.get("id")
            display_order = plan_order.get("display_order")
            
            if plan_id and display_order is not None:
                updates.append({
                    "id": plan_id,
                    "display_order": display_order
                })
        
        if updates:
            return await self.update_many(updates)
        return []
    
    async def _validate_plan_id_unique(self, plan_id: str):
        """Validate that plan_id is unique."""
        existing = await self.get_by_plan_id(plan_id)
        if existing:
            raise ValidationException(
                f"Plan ID '{plan_id}' already exists",
                field="plan_id"
            )
