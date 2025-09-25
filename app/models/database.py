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
