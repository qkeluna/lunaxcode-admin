"""
Pydantic schemas for API requests and responses.
"""

import json
from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, validator
from enum import Enum

# Import enums from database models
from app.models.database import (
    PlanCategory, ButtonVariant, ContactType, FAQCategory, 
    SettingType, ServiceCategory, ProjectType, ServiceUnit
)


# Base schemas
class BaseSchema(BaseModel):
    """Base schema with common fields."""
    
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class BaseResponse(BaseModel):
    """Base response model."""
    
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[dict] = None


class PaginationParams(BaseModel):
    """Pagination parameters."""
    
    page: int = Field(1, ge=1, description="Page number (1-based)")
    size: int = Field(20, ge=1, le=100, description="Page size")
    
    @property
    def offset(self) -> int:
        """Calculate offset for database queries."""
        return (self.page - 1) * self.size


class PaginatedResponse(BaseModel):
    """Paginated response model."""
    
    items: list
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool
    
    @classmethod
    def create(
        cls,
        items: list,
        total: int,
        page: int,
        size: int
    ):
        """Create paginated response."""
        pages = (total + size - 1) // size  # Ceiling division
        
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages,
            has_next=page < pages,
            has_prev=page > 1
        )


# Pricing Plans Schemas
class PricingPlanBase(BaseModel):
    """Base pricing plan schema."""
    
    plan_id: str = Field(..., description="Custom identifier for pricing plan")
    name: str = Field(..., description="Display name of the pricing plan")
    price: str = Field(..., description="Price display text")
    period: Optional[str] = Field("", description="Billing period")
    description: str = Field(..., description="Short description of the plan")
    features: List[str] = Field(..., description="Array of plan features")
    button_text: str = Field("Get Started", description="CTA button text")
    button_variant: ButtonVariant = Field(ButtonVariant.OUTLINE, description="Button style variant")
    popular: bool = Field(False, description="Whether this plan is marked as popular")
    timeline: str = Field(..., description="Delivery timeline")
    display_order: int = Field(0, description="Order for displaying plans")
    category: PlanCategory = Field(PlanCategory.WEB, description="Plan category")
    is_active: bool = Field(True, description="Whether plan is active/visible")
    
    @validator('features', pre=True)
    def parse_features(cls, v):
        """Parse features from JSON string if needed."""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [v]
        return v


class PricingPlanCreate(PricingPlanBase):
    """Schema for creating pricing plans."""
    pass


class PricingPlanUpdate(BaseModel):
    """Schema for updating pricing plans."""
    
    name: Optional[str] = None
    price: Optional[str] = None
    period: Optional[str] = None
    description: Optional[str] = None
    features: Optional[List[str]] = None
    button_text: Optional[str] = None
    button_variant: Optional[ButtonVariant] = None
    popular: Optional[bool] = None
    timeline: Optional[str] = None
    display_order: Optional[int] = None
    category: Optional[PlanCategory] = None
    is_active: Optional[bool] = None


class PricingPlan(PricingPlanBase, BaseSchema):
    """Complete pricing plan schema."""
    pass


# Features Schemas
class FeatureBase(BaseModel):
    """Base feature schema."""
    
    title: str = Field(..., description="Feature title/headline")
    description: str = Field(..., description="Feature description text")
    icon: str = Field(..., description="Lucide icon name")
    color: str = Field(..., description="CSS gradient classes for styling")
    display_order: int = Field(0, description="Order for displaying features")
    is_active: bool = Field(True, description="Whether feature is active/visible")


class FeatureCreate(FeatureBase):
    """Schema for creating features."""
    pass


class FeatureUpdate(BaseModel):
    """Schema for updating features."""
    
    title: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class Feature(FeatureBase, BaseSchema):
    """Complete feature schema."""
    pass


# Process Steps Schemas
class ProcessStepBase(BaseModel):
    """Base process step schema."""
    
    step_number: int = Field(..., description="Step sequence number")
    title: str = Field(..., description="Step title/name")
    description: str = Field(..., description="Step description")
    icon: str = Field(..., description="Lucide icon name for step")
    details: Optional[List[str]] = Field(None, description="Additional details/sub-points array")
    display_order: int = Field(0, description="Order for displaying steps")
    is_active: bool = Field(True, description="Whether step is active/visible")


class ProcessStepCreate(ProcessStepBase):
    """Schema for creating process steps."""
    pass


class ProcessStepUpdate(BaseModel):
    """Schema for updating process steps."""
    
    step_number: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    details: Optional[List[str]] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class ProcessStep(ProcessStepBase, BaseSchema):
    """Complete process step schema."""
    pass


# Hero Section Schemas
class HeroSectionBase(BaseModel):
    """Base hero section schema."""
    
    headline: str = Field(..., description="Main hero headline")
    subheadline: str = Field(..., description="Supporting hero text")
    cta_text: str = Field("Get Started", description="Primary CTA button text")
    cta_variant: ButtonVariant = Field(ButtonVariant.DEFAULT, description="Primary CTA button style")
    secondary_cta_text: Optional[str] = Field(None, description="Secondary CTA button text")
    secondary_cta_variant: Optional[ButtonVariant] = Field(ButtonVariant.OUTLINE, description="Secondary CTA button style")
    background_video: Optional[str] = Field(None, description="URL to background video")
    is_active: bool = Field(True, description="Whether section is active")


class HeroSectionCreate(HeroSectionBase):
    """Schema for creating hero sections."""
    pass


class HeroSectionUpdate(BaseModel):
    """Schema for updating hero sections."""
    
    headline: Optional[str] = None
    subheadline: Optional[str] = None
    cta_text: Optional[str] = None
    cta_variant: Optional[ButtonVariant] = None
    secondary_cta_text: Optional[str] = None
    secondary_cta_variant: Optional[ButtonVariant] = None
    background_video: Optional[str] = None
    is_active: Optional[bool] = None


class HeroSection(HeroSectionBase, BaseSchema):
    """Complete hero section schema."""
    pass


# Testimonials Schemas
class TestimonialBase(BaseModel):
    """Base testimonial schema."""
    
    client_name: str = Field(..., description="Client's full name")
    client_company: Optional[str] = Field(None, description="Client's company name")
    client_role: Optional[str] = Field(None, description="Client's job title/role")
    testimonial: str = Field(..., description="Testimonial content/quote")
    rating: int = Field(5, ge=1, le=5, description="Star rating (1-5)")
    avatar: Optional[str] = Field(None, description="URL to client's avatar image")
    project_type: Optional[ProjectType] = Field(None, description="Type of project")
    display_order: int = Field(0, description="Order for displaying testimonials")
    is_active: bool = Field(True, description="Whether testimonial is active/visible")


class TestimonialCreate(TestimonialBase):
    """Schema for creating testimonials."""
    pass


class TestimonialUpdate(BaseModel):
    """Schema for updating testimonials."""
    
    client_name: Optional[str] = None
    client_company: Optional[str] = None
    client_role: Optional[str] = None
    testimonial: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    avatar: Optional[str] = None
    project_type: Optional[ProjectType] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class Testimonial(TestimonialBase, BaseSchema):
    """Complete testimonial schema."""
    pass


# Contact Info Schemas
class ContactInfoBase(BaseModel):
    """Base contact info schema."""
    
    type: ContactType = Field(..., description="Contact type")
    label: str = Field(..., description="Display label for contact info")
    value: str = Field(..., description="Contact value")
    icon: Optional[str] = Field(None, description="Lucide icon name")
    is_primary: bool = Field(False, description="Whether this is primary contact method")
    display_order: int = Field(0, description="Order for displaying contact info")
    is_active: bool = Field(True, description="Whether contact info is active/visible")


class ContactInfoCreate(ContactInfoBase):
    """Schema for creating contact info."""
    pass


class ContactInfoUpdate(BaseModel):
    """Schema for updating contact info."""
    
    type: Optional[ContactType] = None
    label: Optional[str] = None
    value: Optional[str] = None
    icon: Optional[str] = None
    is_primary: Optional[bool] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class ContactInfo(ContactInfoBase, BaseSchema):
    """Complete contact info schema."""
    pass


# FAQs Schemas
class FAQBase(BaseModel):
    """Base FAQ schema."""
    
    question: str = Field(..., description="FAQ question")
    answer: str = Field(..., description="FAQ answer (supports markdown)")
    category: Optional[FAQCategory] = Field(None, description="FAQ category")
    display_order: int = Field(0, description="Order for displaying FAQs")
    is_active: bool = Field(True, description="Whether FAQ is active/visible")


class FAQCreate(FAQBase):
    """Schema for creating FAQs."""
    pass


class FAQUpdate(BaseModel):
    """Schema for updating FAQs."""
    
    question: Optional[str] = None
    answer: Optional[str] = None
    category: Optional[FAQCategory] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class FAQ(FAQBase, BaseSchema):
    """Complete FAQ schema."""
    pass


# Site Settings Schemas
class SiteSettingBase(BaseModel):
    """Base site setting schema."""
    
    key: str = Field(..., description="Setting key/name")
    value: str = Field(..., description="Setting value")
    type: SettingType = Field(SettingType.TEXT, description="Value type")
    description: Optional[str] = Field(None, description="Setting description")
    is_public: bool = Field(True, description="Whether setting is publicly accessible")


class SiteSettingCreate(SiteSettingBase):
    """Schema for creating site settings."""
    pass


class SiteSettingUpdate(BaseModel):
    """Schema for updating site settings."""
    
    value: Optional[str] = None
    type: Optional[SettingType] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None


class SiteSetting(SiteSettingBase, BaseSchema):
    """Complete site setting schema."""
    pass


# Addon Services Schemas
class AddonServiceBase(BaseModel):
    """Base addon service schema."""
    
    service_id: str = Field(..., description="Custom identifier for add-on service")
    name: str = Field(..., description="Service name")
    price: str = Field(..., description="Price display text")
    description: str = Field(..., description="Service description")
    unit: Optional[ServiceUnit] = Field(None, description="Pricing unit")
    category: ServiceCategory = Field(ServiceCategory.GENERAL, description="Service category")
    icon: Optional[str] = Field(None, description="Lucide icon name")
    popular: bool = Field(False, description="Whether service is popular/featured")
    display_order: int = Field(0, description="Order for displaying services")
    is_active: bool = Field(True, description="Whether service is active/available")


class AddonServiceCreate(AddonServiceBase):
    """Schema for creating addon services."""
    pass


class AddonServiceUpdate(BaseModel):
    """Schema for updating addon services."""
    
    name: Optional[str] = None
    price: Optional[str] = None
    description: Optional[str] = None
    unit: Optional[ServiceUnit] = None
    category: Optional[ServiceCategory] = None
    icon: Optional[str] = None
    popular: Optional[bool] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class AddonService(AddonServiceBase, BaseSchema):
    """Complete addon service schema."""
    pass
