"""
PostgreSQL services for all content models.
"""

import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import (
    Feature as FeatureModel,
    ProcessStep as ProcessStepModel,
    HeroSection as HeroSectionModel,
    Testimonial as TestimonialModel,
    ContactInfo as ContactInfoModel,
    FAQ as FAQModel,
    SiteSetting as SiteSettingModel,
    AddonService as AddonServiceModel,
    FAQCategory, ContactType, ServiceCategory
)
from app.models.schemas import (
    Feature, FeatureCreate, FeatureUpdate,
    ProcessStep, ProcessStepCreate, ProcessStepUpdate,
    HeroSection, HeroSectionCreate, HeroSectionUpdate,
    Testimonial, TestimonialCreate, TestimonialUpdate,
    ContactInfo, ContactInfoCreate, ContactInfoUpdate,
    FAQ, FAQCreate, FAQUpdate,
    SiteSetting, SiteSettingCreate, SiteSettingUpdate,
    AddonService, AddonServiceCreate, AddonServiceUpdate,
    PaginationParams
)
from app.services.postgres_base import PostgresBaseService
from app.core.exceptions import ValidationException

logger = logging.getLogger(__name__)


class PostgresFeaturesService(PostgresBaseService[FeatureModel, FeatureCreate, FeatureUpdate, Feature]):
    """Service for managing features."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(
            model=FeatureModel,
            response_schema=Feature,
            session=session
        )


class PostgresProcessStepsService(PostgresBaseService[ProcessStepModel, ProcessStepCreate, ProcessStepUpdate, ProcessStep]):
    """Service for managing process steps."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(
            model=ProcessStepModel,
            response_schema=ProcessStep,
            session=session
        )


class PostgresHeroSectionService(PostgresBaseService[HeroSectionModel, HeroSectionCreate, HeroSectionUpdate, HeroSection]):
    """Service for managing hero sections."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(
            model=HeroSectionModel,
            response_schema=HeroSection,
            session=session
        )
    
    async def get_active_hero(self) -> Optional[HeroSection]:
        """Get the active hero section."""
        filters = {"is_active": True}
        result = await self.get_all(
            pagination=PaginationParams(page=1, size=1),
            filters=filters
        )
        return result.items[0] if result.items else None


class PostgresTestimonialsService(PostgresBaseService[TestimonialModel, TestimonialCreate, TestimonialUpdate, Testimonial]):
    """Service for managing testimonials."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(
            model=TestimonialModel,
            response_schema=Testimonial,
            session=session
        )
    
    async def get_by_rating(self, min_rating: int = 4) -> List[Testimonial]:
        """Get testimonials by minimum rating."""
        filters = {"is_active": True}
        # Note: We'll need to implement rating filtering in the base service
        # For now, get all and filter in Python (not optimal for large datasets)
        result = await self.get_all(
            pagination=PaginationParams(page=1, size=100),
            filters=filters,
            order_by="display_order"
        )
        return [item for item in result.items if item.rating >= min_rating]


class PostgresContactInfoService(PostgresBaseService[ContactInfoModel, ContactInfoCreate, ContactInfoUpdate, ContactInfo]):
    """Service for managing contact information."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(
            model=ContactInfoModel,
            response_schema=ContactInfo,
            session=session
        )
    
    async def get_by_type(self, contact_type: ContactType) -> List[ContactInfo]:
        """Get contact info by type."""
        filters = {"type": contact_type, "is_active": True}
        result = await self.get_all(
            pagination=PaginationParams(page=1, size=50),
            filters=filters,
            order_by="display_order"
        )
        return result.items
    
    async def get_primary_contacts(self) -> List[ContactInfo]:
        """Get primary contact methods."""
        filters = {"is_primary": True, "is_active": True}
        result = await self.get_all(
            pagination=PaginationParams(page=1, size=10),
            filters=filters,
            order_by="display_order"
        )
        return result.items


class PostgresFAQService(PostgresBaseService[FAQModel, FAQCreate, FAQUpdate, FAQ]):
    """Service for managing FAQs."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(
            model=FAQModel,
            response_schema=FAQ,
            session=session
        )
    
    async def get_by_category(self, category: FAQCategory) -> List[FAQ]:
        """Get FAQs by category."""
        filters = {"category": category, "is_active": True}
        result = await self.get_all(
            pagination=PaginationParams(page=1, size=100),
            filters=filters,
            order_by="display_order"
        )
        return result.items


class PostgresSiteSettingsService(PostgresBaseService[SiteSettingModel, SiteSettingCreate, SiteSettingUpdate, SiteSetting]):
    """Service for managing site settings."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(
            model=SiteSettingModel,
            response_schema=SiteSetting,
            session=session
        )
    
    async def get_by_key(self, key: str) -> Optional[SiteSetting]:
        """Get setting by key."""
        return await self.get_by_field("key", key)
    
    async def get_public_settings(self) -> List[SiteSetting]:
        """Get all public settings."""
        filters = {"is_public": True}
        result = await self.get_all(
            pagination=PaginationParams(page=1, size=100),
            filters=filters,
            order_by="key"
        )
        return result.items
    
    async def create(self, obj_in: SiteSettingCreate) -> SiteSetting:
        """Create a new site setting with key validation."""
        # Validate key uniqueness
        existing = await self.get_by_key(obj_in.key)
        if existing:
            raise ValidationException(
                f"Setting key '{obj_in.key}' already exists",
                field="key"
            )
        
        return await super().create(obj_in)


class PostgresAddonServicesService(PostgresBaseService[AddonServiceModel, AddonServiceCreate, AddonServiceUpdate, AddonService]):
    """Service for managing addon services."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(
            model=AddonServiceModel,
            response_schema=AddonService,
            session=session
        )
    
    async def get_by_service_id(self, service_id: str) -> Optional[AddonService]:
        """Get addon service by service_id."""
        return await self.get_by_field("service_id", service_id)
    
    async def get_by_category(self, category: ServiceCategory) -> List[AddonService]:
        """Get addon services by category."""
        filters = {"category": category, "is_active": True}
        result = await self.get_all(
            pagination=PaginationParams(page=1, size=100),
            filters=filters,
            order_by="display_order"
        )
        return result.items
    
    async def get_popular_services(self, limit: int = 5) -> List[AddonService]:
        """Get popular addon services."""
        filters = {"popular": True, "is_active": True}
        result = await self.get_all(
            pagination=PaginationParams(page=1, size=limit),
            filters=filters,
            order_by="display_order"
        )
        return result.items
    
    async def create(self, obj_in: AddonServiceCreate) -> AddonService:
        """Create a new addon service with service_id validation."""
        # Validate service_id uniqueness
        existing = await self.get_by_service_id(obj_in.service_id)
        if existing:
            raise ValidationException(
                f"Service ID '{obj_in.service_id}' already exists",
                field="service_id"
            )
        
        return await super().create(obj_in)
    
    async def update(self, id: str, obj_in: AddonServiceUpdate) -> AddonService:
        """Update addon service with service_id validation."""
        # If service_id is being updated, validate uniqueness
        if obj_in.service_id is not None:
            existing_service = await self.get_by_service_id(obj_in.service_id)
            if existing_service and existing_service.id != id:
                raise ValidationException(
                    f"Service ID '{obj_in.service_id}' already exists",
                    field="service_id"
                )
        
        return await super().update(id, obj_in)
