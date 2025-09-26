"""
SQLAlchemy models for PostgreSQL database.
"""

from datetime import datetime
from typing import List
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, 
    JSON, Enum as SQLEnum, func, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
import uuid
import enum

from app.database.postgres import Base


# Enums
class PlanCategory(str, enum.Enum):
    WEB = "web"
    MOBILE = "mobile"


class ButtonVariant(str, enum.Enum):
    DEFAULT = "default"
    OUTLINE = "outline"
    SECONDARY = "secondary"
    GHOST = "ghost"


class ContactType(str, enum.Enum):
    EMAIL = "email"
    PHONE = "phone"
    ADDRESS = "address"
    SOCIAL = "social"


class FAQCategory(str, enum.Enum):
    PRICING = "pricing"
    PROCESS = "process"
    GENERAL = "general"
    TECHNICAL = "technical"


class SettingType(str, enum.Enum):
    TEXT = "text"
    NUMBER = "number"
    BOOLEAN = "boolean"
    JSON = "json"


class RateLimitTier(str, enum.Enum):
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"


class ServiceCategory(str, enum.Enum):
    GENERAL = "general"
    SEO = "seo"
    MAINTENANCE = "maintenance"
    INTEGRATION = "integration"


class ProjectType(str, enum.Enum):
    LANDING_PAGE = "landing_page"
    WEB_APP = "web_app"
    MOBILE_APP = "mobile_app"


class ServiceUnit(str, enum.Enum):
    PER_PAGE = "per page"
    PER_MONTH = "per month"
    ONE_TIME = "one-time"


# Onboarding Enums
class ServiceType(str, enum.Enum):
    LANDING_PAGE = "landing_page"
    WEB_APP = "web_app"
    MOBILE_APP = "mobile_app"


class StepName(str, enum.Enum):
    SERVICE_SELECTION = "service_selection"
    BASIC_INFO = "basic_info"
    SERVICE_REQUIREMENTS = "service_requirements"
    REVIEW = "review"
    CONFIRMATION = "confirmation"


class StepStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    ERROR = "error"


class ComponentType(str, enum.Enum):
    FORM = "form"
    SELECTION = "selection"
    REVIEW = "review"
    CONFIRMATION = "confirmation"


class UILayout(str, enum.Enum):
    SINGLE_COLUMN = "single_column"
    TWO_COLUMN = "two_column"
    GRID = "grid"
    CUSTOM = "custom"


class DeviceType(str, enum.Enum):
    DESKTOP = "desktop"
    TABLET = "tablet"
    MOBILE = "mobile"


class ConversionStatus(str, enum.Enum):
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    IN_PROGRESS = "in_progress"


# Base model with common fields
class BaseModel(Base):
    """Base model with common fields for all tables."""
    __abstract__ = True
    
    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


# Pricing Plans Model
class PricingPlan(BaseModel):
    """Pricing plans table."""
    __tablename__ = "pricing_plans"
    
    plan_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    price: Mapped[str] = mapped_column(String(100), nullable=False)
    period: Mapped[str] = mapped_column(String(100), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    features: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    button_text: Mapped[str] = mapped_column(String(100), default="Get Started")
    button_variant: Mapped[ButtonVariant] = mapped_column(
        SQLEnum(ButtonVariant), default=ButtonVariant.OUTLINE
    )
    popular: Mapped[bool] = mapped_column(Boolean, default=False)
    timeline: Mapped[str] = mapped_column(String(200), nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    category: Mapped[PlanCategory] = mapped_column(
        SQLEnum(PlanCategory), default=PlanCategory.WEB
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    __table_args__ = (
        Index('idx_pricing_plans_category_active', 'category', 'is_active'),
        Index('idx_pricing_plans_popular_active', 'popular', 'is_active'),
        Index('idx_pricing_plans_display_order', 'display_order'),
    )


# Features Model
class Feature(BaseModel):
    """Features table."""
    __tablename__ = "features"
    
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    icon: Mapped[str] = mapped_column(String(100), nullable=False)
    color: Mapped[str] = mapped_column(String(200), nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    __table_args__ = (
        Index('idx_features_active_order', 'is_active', 'display_order'),
    )


# Process Steps Model
class ProcessStep(BaseModel):
    """Process steps table."""
    __tablename__ = "process_steps"
    
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    icon: Mapped[str] = mapped_column(String(100), nullable=False)
    details: Mapped[List[str]] = mapped_column(JSON, nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    __table_args__ = (
        Index('idx_process_steps_active_order', 'is_active', 'display_order'),
        Index('idx_process_steps_step_number', 'step_number'),
    )


# Hero Section Model
class HeroSection(BaseModel):
    """Hero sections table."""
    __tablename__ = "hero_sections"
    
    headline: Mapped[str] = mapped_column(Text, nullable=False)
    subheadline: Mapped[str] = mapped_column(Text, nullable=False)
    cta_text: Mapped[str] = mapped_column(String(100), default="Get Started")
    cta_variant: Mapped[ButtonVariant] = mapped_column(
        SQLEnum(ButtonVariant), default=ButtonVariant.DEFAULT
    )
    secondary_cta_text: Mapped[str] = mapped_column(String(100), nullable=True)
    secondary_cta_variant: Mapped[ButtonVariant] = mapped_column(
        SQLEnum(ButtonVariant), default=ButtonVariant.OUTLINE, nullable=True
    )
    background_video: Mapped[str] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    __table_args__ = (
        Index('idx_hero_sections_active', 'is_active'),
    )


# Testimonials Model
class Testimonial(BaseModel):
    """Testimonials table."""
    __tablename__ = "testimonials"
    
    client_name: Mapped[str] = mapped_column(String(200), nullable=False)
    client_company: Mapped[str] = mapped_column(String(200), nullable=True)
    client_role: Mapped[str] = mapped_column(String(200), nullable=True)
    testimonial: Mapped[str] = mapped_column(Text, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    avatar: Mapped[str] = mapped_column(String(500), nullable=True)
    project_type: Mapped[ProjectType] = mapped_column(
        SQLEnum(ProjectType), nullable=True
    )
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    __table_args__ = (
        Index('idx_testimonials_active_order', 'is_active', 'display_order'),
        Index('idx_testimonials_rating', 'rating'),
    )


# Contact Info Model
class ContactInfo(BaseModel):
    """Contact information table."""
    __tablename__ = "contact_info"
    
    type: Mapped[ContactType] = mapped_column(SQLEnum(ContactType), nullable=False)
    label: Mapped[str] = mapped_column(String(200), nullable=False)
    value: Mapped[str] = mapped_column(String(500), nullable=False)
    icon: Mapped[str] = mapped_column(String(100), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    __table_args__ = (
        Index('idx_contact_info_type_active', 'type', 'is_active'),
        Index('idx_contact_info_primary', 'is_primary'),
        Index('idx_contact_info_display_order', 'display_order'),
    )


# FAQs Model
class FAQ(BaseModel):
    """Frequently Asked Questions table."""
    __tablename__ = "faqs"
    
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[FAQCategory] = mapped_column(
        SQLEnum(FAQCategory), nullable=True
    )
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    __table_args__ = (
        Index('idx_faqs_category_active', 'category', 'is_active'),
        Index('idx_faqs_active_order', 'is_active', 'display_order'),
    )


# Site Settings Model
class SiteSetting(BaseModel):
    """Site settings table."""
    __tablename__ = "site_settings"
    
    key: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[SettingType] = mapped_column(
        SQLEnum(SettingType), default=SettingType.TEXT
    )
    description: Mapped[str] = mapped_column(Text, nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    
    __table_args__ = (
        Index('idx_site_settings_public', 'is_public'),
        Index('idx_site_settings_type', 'type'),
    )


# Addon Services Model
class AddonService(BaseModel):
    """Add-on services table."""
    __tablename__ = "addon_services"
    
    service_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    price: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    unit: Mapped[ServiceUnit] = mapped_column(SQLEnum(ServiceUnit), nullable=True)
    category: Mapped[ServiceCategory] = mapped_column(
        SQLEnum(ServiceCategory), default=ServiceCategory.GENERAL
    )
    icon: Mapped[str] = mapped_column(String(100), nullable=True)
    popular: Mapped[bool] = mapped_column(Boolean, default=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    __table_args__ = (
        Index('idx_addon_services_category_active', 'category', 'is_active'),
        Index('idx_addon_services_popular_active', 'popular', 'is_active'),
        Index('idx_addon_services_display_order', 'display_order'),
    )


# Onboarding Steps Model
class OnboardingStep(BaseModel):
    """Onboarding steps configuration table."""
    __tablename__ = "onboarding_steps"
    
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    step_name: Mapped[StepName] = mapped_column(SQLEnum(StepName), nullable=False)
    step_title: Mapped[str] = mapped_column(String(200), nullable=False)
    step_description: Mapped[str] = mapped_column(Text, nullable=True)
    validation_schema: Mapped[dict] = mapped_column(JSON, nullable=True)
    required_fields: Mapped[List[str]] = mapped_column(JSON, nullable=True)
    optional_fields: Mapped[List[str]] = mapped_column(JSON, nullable=True)
    component_type: Mapped[ComponentType] = mapped_column(SQLEnum(ComponentType), nullable=False)
    form_config: Mapped[dict] = mapped_column(JSON, nullable=True)
    ui_layout: Mapped[UILayout] = mapped_column(SQLEnum(UILayout), default=UILayout.SINGLE_COLUMN)
    next_step_conditions: Mapped[dict] = mapped_column(JSON, nullable=True)
    skip_conditions: Mapped[dict] = mapped_column(JSON, nullable=True)
    back_allowed: Mapped[bool] = mapped_column(Boolean, default=True)
    service_types: Mapped[List[str]] = mapped_column(JSON, nullable=True)
    is_conditional: Mapped[bool] = mapped_column(Boolean, default=False)
    conditional_logic: Mapped[dict] = mapped_column(JSON, nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    progress_weight: Mapped[int] = mapped_column(Integer, default=1)
    estimated_time: Mapped[int] = mapped_column(Integer, nullable=True)  # minutes
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_required: Mapped[bool] = mapped_column(Boolean, default=True)
    
    __table_args__ = (
        Index('idx_onboarding_steps_name_active', 'step_name', 'is_active'),
        Index('idx_onboarding_steps_number_active', 'step_number', 'is_active'),
        Index('idx_onboarding_steps_display_order', 'display_order'),
        # Note: Cannot index JSON columns directly in PostgreSQL without operator class
    )


# Onboarding Step Progress Model
class OnboardingStepProgress(BaseModel):
    """Onboarding step progress tracking table."""
    __tablename__ = "onboarding_step_progress"
    
    submission_id: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    step_id: Mapped[str] = mapped_column(String(100), nullable=False)
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    step_name: Mapped[StepName] = mapped_column(SQLEnum(StepName), nullable=False)
    status: Mapped[StepStatus] = mapped_column(SQLEnum(StepStatus), default=StepStatus.PENDING)
    step_data: Mapped[dict] = mapped_column(JSON, nullable=True)
    validation_errors: Mapped[List[dict]] = mapped_column(JSON, nullable=True)
    user_input: Mapped[dict] = mapped_column(JSON, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    time_spent: Mapped[int] = mapped_column(Integer, nullable=True)  # seconds
    attempt_count: Mapped[int] = mapped_column(Integer, default=1)
    previous_step_id: Mapped[str] = mapped_column(String(100), nullable=True)
    next_step_id: Mapped[str] = mapped_column(String(100), nullable=True)
    navigation_history: Mapped[List[dict]] = mapped_column(JSON, nullable=True)
    user_agent: Mapped[str] = mapped_column(Text, nullable=True)
    device_type: Mapped[DeviceType] = mapped_column(SQLEnum(DeviceType), nullable=True)
    exited_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    
    __table_args__ = (
        Index('idx_step_progress_submission_step', 'submission_id', 'step_id'),
        Index('idx_step_progress_status', 'status'),
        Index('idx_step_progress_step_name', 'step_name'),
        Index('idx_step_progress_device_type', 'device_type'),
        Index('idx_step_progress_started_at', 'started_at'),
    )


# Onboarding Analytics Model
class OnboardingAnalytics(BaseModel):
    """Onboarding analytics and performance data table."""
    __tablename__ = "onboarding_analytics"
    
    session_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    submission_id: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    total_steps: Mapped[int] = mapped_column(Integer, nullable=False)
    completed_steps: Mapped[int] = mapped_column(Integer, default=0)
    skipped_steps: Mapped[int] = mapped_column(Integer, default=0)
    error_steps: Mapped[int] = mapped_column(Integer, default=0)
    total_time_spent: Mapped[int] = mapped_column(Integer, default=0)  # seconds
    average_step_time: Mapped[int] = mapped_column(Integer, default=0)  # seconds
    fastest_step: Mapped[str] = mapped_column(String(100), nullable=True)
    slowest_step: Mapped[str] = mapped_column(String(100), nullable=True)
    completion_rate: Mapped[int] = mapped_column(Integer, default=0)  # percentage 0-100
    abandoned_at: Mapped[str] = mapped_column(String(100), nullable=True)
    conversion_status: Mapped[ConversionStatus] = mapped_column(
        SQLEnum(ConversionStatus), default=ConversionStatus.IN_PROGRESS
    )
    back_navigation_count: Mapped[int] = mapped_column(Integer, default=0)
    error_count: Mapped[int] = mapped_column(Integer, default=0)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    help_requested: Mapped[bool] = mapped_column(Boolean, default=False)
    performance_score: Mapped[int] = mapped_column(Integer, default=0)  # 0-100
    user_experience_score: Mapped[int] = mapped_column(Integer, default=0)  # 0-100
    technical_issues: Mapped[List[dict]] = mapped_column(JSON, nullable=True)
    user_agent: Mapped[str] = mapped_column(Text, nullable=True)
    device_type: Mapped[DeviceType] = mapped_column(SQLEnum(DeviceType), nullable=True)
    browser_name: Mapped[str] = mapped_column(String(100), nullable=True)
    operating_system: Mapped[str] = mapped_column(String(100), nullable=True)
    screen_resolution: Mapped[str] = mapped_column(String(50), nullable=True)
    
    __table_args__ = (
        Index('idx_analytics_session_id', 'session_id'),
        Index('idx_analytics_submission_id', 'submission_id'),
        Index('idx_analytics_conversion_status', 'conversion_status'),
        Index('idx_analytics_completion_rate', 'completion_rate'),
        Index('idx_analytics_device_type', 'device_type'),
        Index('idx_analytics_created_at', 'created_at'),
    )


# API Key Model
class APIKey(BaseModel):
    """API key management table for external access."""
    __tablename__ = "api_keys"

    key_hash: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    key_prefix: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    scopes: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    rate_limit_tier: Mapped[RateLimitTier] = mapped_column(
        SQLEnum(RateLimitTier), default=RateLimitTier.BASIC, nullable=False
    )
    requests_per_hour: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    requests_per_day: Mapped[int] = mapped_column(Integer, default=2400, nullable=False)
    ip_whitelist: Mapped[List[str]] = mapped_column(JSON, nullable=True, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_used_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    request_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_by: Mapped[str] = mapped_column(String(100), nullable=True)  # user email or system

    __table_args__ = (
        Index('idx_apikey_hash', 'key_hash'),
        Index('idx_apikey_prefix', 'key_prefix'),
        Index('idx_apikey_active', 'is_active'),
        Index('idx_apikey_tier', 'rate_limit_tier'),
        Index('idx_apikey_created_by', 'created_by'),
        Index('idx_apikey_last_used', 'last_used_at'),
    )
