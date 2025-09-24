"""
Pricing plans service with business logic.
"""

import logging
from typing import List, Optional
from app.database.xata import XataDB
from app.models.content import PricingPlan, PricingPlanCreate, PricingPlanUpdate, PlanCategory
from app.services.base import BaseService
from app.core.exceptions import ValidationException

logger = logging.getLogger(__name__)


class PricingPlansService(BaseService[PricingPlan, PricingPlanCreate, PricingPlanUpdate]):
    """Service for managing pricing plans."""
    
    def __init__(self, db: XataDB):
        super().__init__(
            db=db,
            table_name="pricing_plans",
            model_class=PricingPlan,
            create_model_class=PricingPlanCreate,
            update_model_class=PricingPlanUpdate
        )
    
    async def create(self, data: PricingPlanCreate, record_id: Optional[str] = None) -> PricingPlan:
        """Create a new pricing plan with validation."""
        # Validate planId uniqueness
        await self._validate_plan_id_unique(data.planId)
        
        return await super().create(data, record_id)
    
    async def update(self, record_id: str, data: PricingPlanUpdate) -> PricingPlan:
        """Update pricing plan with validation."""
        # If planId is being updated, validate uniqueness
        if data.planId is not None:
            # Check if another plan already uses this planId
            existing_plans = await self.get_by_plan_id(data.planId)
            if existing_plans and existing_plans.xata_id != record_id:
                raise ValidationException(
                    f"Plan ID '{data.planId}' already exists",
                    field="planId"
                )
        
        return await super().update(record_id, data)
    
    async def get_by_plan_id(self, plan_id: str) -> Optional[PricingPlan]:
        """Get pricing plan by planId."""
        try:
            result = await self.db.query_records(
                table=self.table_name,
                filter_conditions={"planId": plan_id},
                page_size=1
            )
            
            records = result.get("records", [])
            if records:
                return PricingPlan(**records[0])
            return None
            
        except Exception as e:
            logger.error(f"Error getting pricing plan by planId {plan_id}: {e}")
            return None
    
    async def get_by_category(self, category: PlanCategory) -> List[PricingPlan]:
        """Get pricing plans by category."""
        try:
            result = await self.db.query_records(
                table=self.table_name,
                filter_conditions={
                    "category": category.value,
                    "isActive": True
                },
                sort=[{"displayOrder": "asc"}],
                page_size=100  # Get all plans for a category
            )
            
            return [PricingPlan(**record) for record in result.get("records", [])]
            
        except Exception as e:
            logger.error(f"Error getting pricing plans by category {category}: {e}")
            return []
    
    async def get_popular_plans(self, limit: int = 3) -> List[PricingPlan]:
        """Get popular pricing plans."""
        try:
            result = await self.db.query_records(
                table=self.table_name,
                filter_conditions={
                    "popular": True,
                    "isActive": True
                },
                sort=[{"displayOrder": "asc"}],
                page_size=limit
            )
            
            return [PricingPlan(**record) for record in result.get("records", [])]
            
        except Exception as e:
            logger.error(f"Error getting popular pricing plans: {e}")
            return []
    
    async def set_popular_status(self, record_id: str, popular: bool) -> PricingPlan:
        """Set popular status for a pricing plan."""
        data = PricingPlanUpdate(popular=popular)
        return await self.update(record_id, data)
    
    async def reorder_plans(self, plan_orders: List[dict]) -> List[PricingPlan]:
        """
        Reorder pricing plans.
        
        Args:
            plan_orders: List of dicts with 'id' and 'displayOrder' keys
        
        Returns:
            List of updated pricing plans
        """
        updated_plans = []
        
        for plan_order in plan_orders:
            plan_id = plan_order.get("id")
            display_order = plan_order.get("displayOrder")
            
            if plan_id and display_order is not None:
                try:
                    data = PricingPlanUpdate(displayOrder=display_order)
                    updated_plan = await self.update(plan_id, data)
                    updated_plans.append(updated_plan)
                except Exception as e:
                    logger.error(f"Error updating order for plan {plan_id}: {e}")
        
        return updated_plans
    
    async def _validate_plan_id_unique(self, plan_id: str):
        """Validate that planId is unique."""
        existing = await self.get_by_plan_id(plan_id)
        if existing:
            raise ValidationException(
                f"Plan ID '{plan_id}' already exists",
                field="planId"
            )
