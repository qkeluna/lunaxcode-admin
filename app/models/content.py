"""
Pydantic models for content tables based on Xata schema.
"""

import json
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, validator
from enum import Enum

from app.models.base import XataRecord


# Enums for validation
class PlanCategory(str, Enum):
    WEB = "web"
    MOBILE = "mobile"


class ButtonVariant(str, Enum):
    DEFAULT = "default"
    OUTLINE = "outline"
    SECONDARY = "secondary"
    GHOST = "ghost"


class ContactType(str, Enum):
    EMAIL = "email"
    PHONE = "phone"
    ADDRESS = "address"
    SOCIAL = "social"


class FAQCategory(str, Enum):
    PRICING = "pricing"
    PROCESS = "process"
    GENERAL = "general"
    TECHNICAL = "technical"


class SettingType(str, Enum):
    TEXT = "text"
    NUMBER = "number"
    BOOLEAN = "boolean"
    JSON = "json"


class ServiceCategory(str, Enum):
    GENERAL = "general"
    SEO = "seo"
    MAINTENANCE = "maintenance"
    INTEGRATION = "integration"


class ProjectType(str, Enum):
    LANDING_PAGE = "landing_page"
    WEB_APP = "web_app"
    MOBILE_APP = "mobile_app"


class ServiceUnit(str, Enum):
    PER_PAGE = "per page"
    PER_MONTH = "per month"
    ONE_TIME = "one-time"


# Pricing Plans Models
class PricingPlanBase(BaseModel):
    """Base pricing plan model."""
    
    planId: str = Field(..., description="Custom identifier for pricing plan")
    name: str = Field(..., description="Display name of the pricing plan")
    price: str = Field(..., description="Price display text")
    period: Optional[str] = Field("", description="Billing period")
    description: str = Field(..., description="Short description of the plan")
    features: List[str] = Field(..., description="Array of plan features")
    buttonText: str = Field("Get Started", description="CTA button text")
    buttonVariant: ButtonVariant = Field(ButtonVariant.OUTLINE, description="Button style variant")
    popular: bool = Field(False, description="Whether this plan is marked as popular")
    timeline: str = Field(..., description="Delivery timeline")
    displayOrder: int = Field(0, description="Order for displaying plans")
    category: PlanCategory = Field(PlanCategory.WEB, description="Plan category")
    isActive: bool = Field(True, description="Whether plan is active/visible")
    
    @validator('features', pre=True)
    def parse_features(cls, v):
        """Parse features from JSON string if needed."""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                # If it's not valid JSON, return as single-item list
                return [v]
        return v


class PricingPlanCreate(PricingPlanBase):
    """Model for creating pricing plans."""
    pass


class PricingPlanUpdate(BaseModel):
    """Model for updating pricing plans."""
    
    name: Optional[str] = None
    price: Optional[str] = None
    period: Optional[str] = None
    description: Optional[str] = None
    features: Optional[List[str]] = None
    buttonText: Optional[str] = None
    buttonVariant: Optional[ButtonVariant] = None
    popular: Optional[bool] = None
    timeline: Optional[str] = None
    displayOrder: Optional[int] = None
    category: Optional[PlanCategory] = None
    isActive: Optional[bool] = None


class PricingPlan(PricingPlanBase, XataRecord):
    """Complete pricing plan model with Xata fields."""
    pass


# Features Models
class FeatureBase(BaseModel):
    """Base feature model."""
    
    title: str = Field(..., description="Feature title/headline")
    description: str = Field(..., description="Feature description text")
    icon: str = Field(..., description="Lucide icon name")
    color: str = Field(..., description="CSS gradient classes for styling")
    displayOrder: int = Field(0, description="Order for displaying features")
    isActive: bool = Field(True, description="Whether feature is active/visible")


class FeatureCreate(FeatureBase):
    """Model for creating features."""
    pass


class FeatureUpdate(BaseModel):
    """Model for updating features."""
    
    title: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    displayOrder: Optional[int] = None
    isActive: Optional[bool] = None


class Feature(FeatureBase, XataRecord):
    """Complete feature model with Xata fields."""
    pass


# Process Steps Models
class ProcessStepBase(BaseModel):
    """Base process step model."""
    
    stepNumber: int = Field(..., description="Step sequence number")
    title: str = Field(..., description="Step title/name")
    description: str = Field(..., description="Step description")
    icon: str = Field(..., description="Lucide icon name for step")
    details: Optional[List[str]] = Field(None, description="Additional details/sub-points array")
    displayOrder: int = Field(0, description="Order for displaying steps")
    isActive: bool = Field(True, description="Whether step is active/visible")


class ProcessStepCreate(ProcessStepBase):
    """Model for creating process steps."""
    pass


class ProcessStepUpdate(BaseModel):
    """Model for updating process steps."""
    
    stepNumber: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    details: Optional[List[str]] = None
    displayOrder: Optional[int] = None
    isActive: Optional[bool] = None


class ProcessStep(ProcessStepBase, XataRecord):
    """Complete process step model with Xata fields."""
    pass


# Hero Section Models
class HeroSectionBase(BaseModel):
    """Base hero section model."""
    
    headline: str = Field(..., description="Main hero headline")
    subheadline: str = Field(..., description="Supporting hero text")
    ctaText: str = Field("Get Started", description="Primary CTA button text")
    ctaVariant: ButtonVariant = Field(ButtonVariant.DEFAULT, description="Primary CTA button style")
    secondaryCtaText: Optional[str] = Field(None, description="Secondary CTA button text")
    secondaryCtaVariant: Optional[ButtonVariant] = Field(ButtonVariant.OUTLINE, description="Secondary CTA button style")
    backgroundVideo: Optional[str] = Field(None, description="URL to background video")
    isActive: bool = Field(True, description="Whether section is active")


class HeroSectionCreate(HeroSectionBase):
    """Model for creating hero sections."""
    pass


class HeroSectionUpdate(BaseModel):
    """Model for updating hero sections."""
    
    headline: Optional[str] = None
    subheadline: Optional[str] = None
    ctaText: Optional[str] = None
    ctaVariant: Optional[ButtonVariant] = None
    secondaryCtaText: Optional[str] = None
    secondaryCtaVariant: Optional[ButtonVariant] = None
    backgroundVideo: Optional[str] = None
    isActive: Optional[bool] = None


class HeroSection(HeroSectionBase, XataRecord):
    """Complete hero section model with Xata fields."""
    pass


# Testimonials Models
class TestimonialBase(BaseModel):
    """Base testimonial model."""
    
    clientName: str = Field(..., description="Client's full name")
    clientCompany: Optional[str] = Field(None, description="Client's company name")
    clientRole: Optional[str] = Field(None, description="Client's job title/role")
    testimonial: str = Field(..., description="Testimonial content/quote")
    rating: int = Field(5, ge=1, le=5, description="Star rating (1-5)")
    avatar: Optional[str] = Field(None, description="URL to client's avatar image")
    projectType: Optional[ProjectType] = Field(None, description="Type of project")
    displayOrder: int = Field(0, description="Order for displaying testimonials")
    isActive: bool = Field(True, description="Whether testimonial is active/visible")


class TestimonialCreate(TestimonialBase):
    """Model for creating testimonials."""
    pass


class TestimonialUpdate(BaseModel):
    """Model for updating testimonials."""
    
    clientName: Optional[str] = None
    clientCompany: Optional[str] = None
    clientRole: Optional[str] = None
    testimonial: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    avatar: Optional[str] = None
    projectType: Optional[ProjectType] = None
    displayOrder: Optional[int] = None
    isActive: Optional[bool] = None


class Testimonial(TestimonialBase, XataRecord):
    """Complete testimonial model with Xata fields."""
    pass


# Contact Info Models
class ContactInfoBase(BaseModel):
    """Base contact info model."""
    
    type: ContactType = Field(..., description="Contact type")
    label: str = Field(..., description="Display label for contact info")
    value: str = Field(..., description="Contact value")
    icon: Optional[str] = Field(None, description="Lucide icon name")
    isPrimary: bool = Field(False, description="Whether this is primary contact method")
    displayOrder: int = Field(0, description="Order for displaying contact info")
    isActive: bool = Field(True, description="Whether contact info is active/visible")


class ContactInfoCreate(ContactInfoBase):
    """Model for creating contact info."""
    pass


class ContactInfoUpdate(BaseModel):
    """Model for updating contact info."""
    
    type: Optional[ContactType] = None
    label: Optional[str] = None
    value: Optional[str] = None
    icon: Optional[str] = None
    isPrimary: Optional[bool] = None
    displayOrder: Optional[int] = None
    isActive: Optional[bool] = None


class ContactInfo(ContactInfoBase, XataRecord):
    """Complete contact info model with Xata fields."""
    pass


# FAQs Models
class FAQBase(BaseModel):
    """Base FAQ model."""
    
    question: str = Field(..., description="FAQ question")
    answer: str = Field(..., description="FAQ answer (supports markdown)")
    category: Optional[FAQCategory] = Field(None, description="FAQ category")
    displayOrder: int = Field(0, description="Order for displaying FAQs")
    isActive: bool = Field(True, description="Whether FAQ is active/visible")


class FAQCreate(FAQBase):
    """Model for creating FAQs."""
    pass


class FAQUpdate(BaseModel):
    """Model for updating FAQs."""
    
    question: Optional[str] = None
    answer: Optional[str] = None
    category: Optional[FAQCategory] = None
    displayOrder: Optional[int] = None
    isActive: Optional[bool] = None


class FAQ(FAQBase, XataRecord):
    """Complete FAQ model with Xata fields."""
    pass


# Site Settings Models
class SiteSettingBase(BaseModel):
    """Base site setting model."""
    
    key: str = Field(..., description="Setting key/name")
    value: str = Field(..., description="Setting value")
    type: SettingType = Field(SettingType.TEXT, description="Value type")
    description: Optional[str] = Field(None, description="Setting description")
    isPublic: bool = Field(True, description="Whether setting is publicly accessible")


class SiteSettingCreate(SiteSettingBase):
    """Model for creating site settings."""
    pass


class SiteSettingUpdate(BaseModel):
    """Model for updating site settings."""
    
    value: Optional[str] = None
    type: Optional[SettingType] = None
    description: Optional[str] = None
    isPublic: Optional[bool] = None


class SiteSetting(SiteSettingBase, XataRecord):
    """Complete site setting model with Xata fields."""
    pass


# Addon Services Models
class AddonServiceBase(BaseModel):
    """Base addon service model."""
    
    serviceId: str = Field(..., description="Custom identifier for add-on service")
    name: str = Field(..., description="Service name")
    price: str = Field(..., description="Price display text")
    description: str = Field(..., description="Service description")
    unit: Optional[ServiceUnit] = Field(None, description="Pricing unit")
    category: ServiceCategory = Field(ServiceCategory.GENERAL, description="Service category")
    icon: Optional[str] = Field(None, description="Lucide icon name")
    popular: bool = Field(False, description="Whether service is popular/featured")
    displayOrder: int = Field(0, description="Order for displaying services")
    isActive: bool = Field(True, description="Whether service is active/available")


class AddonServiceCreate(AddonServiceBase):
    """Model for creating addon services."""
    pass


class AddonServiceUpdate(BaseModel):
    """Model for updating addon services."""
    
    name: Optional[str] = None
    price: Optional[str] = None
    description: Optional[str] = None
    unit: Optional[ServiceUnit] = None
    category: Optional[ServiceCategory] = None
    icon: Optional[str] = None
    popular: Optional[bool] = None
    displayOrder: Optional[int] = None
    isActive: Optional[bool] = None


class AddonService(AddonServiceBase, XataRecord):
    """Complete addon service model with Xata fields."""
    pass
