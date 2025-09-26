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
    SettingType, ServiceCategory, ProjectType, ServiceUnit,
    ServiceType, StepName, StepStatus, ComponentType, UILayout,
    DeviceType, ConversionStatus, UserRole, OAuthProvider
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


# Onboarding Schemas
class OnboardingStepBase(BaseModel):
    """Base onboarding step schema."""
    
    step_number: int = Field(..., description="Sequential step number")
    step_name: StepName = Field(..., description="Step name enum")
    step_title: str = Field(..., description="Display title for the step")
    step_description: Optional[str] = Field(None, description="Optional step description")
    validation_schema: Optional[Dict[str, Any]] = Field(None, description="JSON validation schema")
    required_fields: Optional[List[str]] = Field(None, description="List of required field names")
    optional_fields: Optional[List[str]] = Field(None, description="List of optional field names")
    component_type: ComponentType = Field(..., description="UI component type")
    form_config: Optional[Dict[str, Any]] = Field(None, description="Form configuration object")
    ui_layout: UILayout = Field(UILayout.SINGLE_COLUMN, description="UI layout type")
    next_step_conditions: Optional[Dict[str, Any]] = Field(None, description="Conditions for next step")
    skip_conditions: Optional[Dict[str, Any]] = Field(None, description="Conditions to skip step")
    back_allowed: bool = Field(True, description="Whether back navigation is allowed")
    service_types: Optional[List[str]] = Field(None, description="Applicable service types")
    is_conditional: bool = Field(False, description="Whether step is conditionally displayed")
    conditional_logic: Optional[Dict[str, Any]] = Field(None, description="Conditional logic object")
    display_order: int = Field(0, description="Display order")
    progress_weight: int = Field(1, description="Progress bar weight")
    estimated_time: Optional[int] = Field(None, description="Estimated completion time in minutes")
    is_active: bool = Field(True, description="Whether step is active")
    is_required: bool = Field(True, description="Whether step is required")


class OnboardingStepCreate(OnboardingStepBase):
    """Schema for creating onboarding steps."""
    pass


class OnboardingStepUpdate(BaseModel):
    """Schema for updating onboarding steps."""
    
    step_number: Optional[int] = None
    step_name: Optional[StepName] = None
    step_title: Optional[str] = None
    step_description: Optional[str] = None
    validation_schema: Optional[Dict[str, Any]] = None
    required_fields: Optional[List[str]] = None
    optional_fields: Optional[List[str]] = None
    component_type: Optional[ComponentType] = None
    form_config: Optional[Dict[str, Any]] = None
    ui_layout: Optional[UILayout] = None
    next_step_conditions: Optional[Dict[str, Any]] = None
    skip_conditions: Optional[Dict[str, Any]] = None
    back_allowed: Optional[bool] = None
    service_types: Optional[List[str]] = None
    is_conditional: Optional[bool] = None
    conditional_logic: Optional[Dict[str, Any]] = None
    display_order: Optional[int] = None
    progress_weight: Optional[int] = None
    estimated_time: Optional[int] = None
    is_active: Optional[bool] = None
    is_required: Optional[bool] = None


class OnboardingStep(OnboardingStepBase, BaseSchema):
    """Complete onboarding step schema."""
    pass


class OnboardingStepProgressBase(BaseModel):
    """Base onboarding step progress schema."""
    
    submission_id: Optional[str] = Field(None, description="Reference to submission")
    step_id: str = Field(..., description="Reference to onboarding step")
    step_number: int = Field(..., description="Step sequence number")
    step_name: StepName = Field(..., description="Step name")
    status: StepStatus = Field(StepStatus.PENDING, description="Current step status")
    step_data: Optional[Dict[str, Any]] = Field(None, description="Data collected in step")
    validation_errors: Optional[List[Dict[str, Any]]] = Field(None, description="Validation errors")
    user_input: Optional[Dict[str, Any]] = Field(None, description="Raw user input")
    started_at: Optional[datetime] = Field(None, description="When step was started")
    completed_at: Optional[datetime] = Field(None, description="When step was completed")
    time_spent: Optional[int] = Field(None, description="Time spent in seconds")
    attempt_count: int = Field(1, description="Number of attempts")
    previous_step_id: Optional[str] = Field(None, description="Previous step reference")
    next_step_id: Optional[str] = Field(None, description="Next step reference")
    navigation_history: Optional[List[Dict[str, Any]]] = Field(None, description="Navigation events")
    user_agent: Optional[str] = Field(None, description="User agent string")
    device_type: Optional[DeviceType] = Field(None, description="Device type")
    exited_at: Optional[datetime] = Field(None, description="If user exited without completing")


class OnboardingStepProgressCreate(OnboardingStepProgressBase):
    """Schema for creating step progress records."""
    pass


class OnboardingStepProgressUpdate(BaseModel):
    """Schema for updating step progress."""
    
    status: Optional[StepStatus] = None
    step_data: Optional[Dict[str, Any]] = None
    validation_errors: Optional[List[Dict[str, Any]]] = None
    user_input: Optional[Dict[str, Any]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    time_spent: Optional[int] = None
    attempt_count: Optional[int] = None
    navigation_history: Optional[List[Dict[str, Any]]] = None
    exited_at: Optional[datetime] = None


class OnboardingStepProgress(OnboardingStepProgressBase, BaseSchema):
    """Complete step progress schema."""
    pass


class OnboardingAnalyticsBase(BaseModel):
    """Base onboarding analytics schema."""
    
    session_id: str = Field(..., description="Session identifier")
    submission_id: Optional[str] = Field(None, description="Submission reference")
    total_steps: int = Field(..., description="Total number of steps")
    completed_steps: int = Field(0, description="Number of completed steps")
    skipped_steps: int = Field(0, description="Number of skipped steps")
    error_steps: int = Field(0, description="Number of steps with errors")
    total_time_spent: int = Field(0, description="Total time in seconds")
    average_step_time: int = Field(0, description="Average time per step")
    fastest_step: Optional[str] = Field(None, description="Fastest completed step")
    slowest_step: Optional[str] = Field(None, description="Slowest completed step")
    completion_rate: int = Field(0, description="Completion percentage (0-100)")
    abandoned_at: Optional[str] = Field(None, description="Step where user abandoned")
    conversion_status: ConversionStatus = Field(ConversionStatus.IN_PROGRESS, description="Conversion status")
    back_navigation_count: int = Field(0, description="Number of back navigations")
    error_count: int = Field(0, description="Total error count")
    retry_count: int = Field(0, description="Total retry count")
    help_requested: bool = Field(False, description="Whether help was requested")
    performance_score: int = Field(0, description="Performance score (0-100)")
    user_experience_score: int = Field(0, description="UX score (0-100)")
    technical_issues: Optional[List[Dict[str, Any]]] = Field(None, description="Technical issues")
    user_agent: Optional[str] = Field(None, description="User agent string")
    device_type: Optional[DeviceType] = Field(None, description="Device type")
    browser_name: Optional[str] = Field(None, description="Browser name")
    operating_system: Optional[str] = Field(None, description="Operating system")
    screen_resolution: Optional[str] = Field(None, description="Screen resolution")


class OnboardingAnalyticsCreate(OnboardingAnalyticsBase):
    """Schema for creating analytics records."""
    pass


class OnboardingAnalyticsUpdate(BaseModel):
    """Schema for updating analytics."""
    
    completed_steps: Optional[int] = None
    skipped_steps: Optional[int] = None
    error_steps: Optional[int] = None
    total_time_spent: Optional[int] = None
    average_step_time: Optional[int] = None
    fastest_step: Optional[str] = None
    slowest_step: Optional[str] = None
    completion_rate: Optional[int] = None
    abandoned_at: Optional[str] = None
    conversion_status: Optional[ConversionStatus] = None
    back_navigation_count: Optional[int] = None
    error_count: Optional[int] = None
    retry_count: Optional[int] = None
    help_requested: Optional[bool] = None
    performance_score: Optional[int] = None
    user_experience_score: Optional[int] = None
    technical_issues: Optional[List[Dict[str, Any]]] = None


class OnboardingAnalytics(OnboardingAnalyticsBase, BaseSchema):
    """Complete analytics schema."""
    pass


# Flow Management Schemas
class StartOnboardingFlowRequest(BaseModel):
    """Request to start new onboarding flow."""
    
    service_type: ServiceType = Field(..., description="Selected service type")
    user_agent: Optional[str] = Field(None, description="User agent string")
    device_type: Optional[DeviceType] = Field(None, description="Device type")
    screen_resolution: Optional[str] = Field(None, description="Screen resolution")


class SubmitStepDataRequest(BaseModel):
    """Request to submit step data."""
    
    session_id: str = Field(..., description="Session identifier")
    step_id: str = Field(..., description="Step identifier")
    step_data: Dict[str, Any] = Field(..., description="Step form data")
    time_spent: Optional[int] = Field(None, description="Time spent in seconds")
    device_type: Optional[DeviceType] = Field(None, description="Device type")
    user_agent: Optional[str] = Field(None, description="User agent")


class ValidationResult(BaseModel):
    """Validation result schema."""
    
    is_valid: bool = Field(..., description="Whether validation passed")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="Validation errors")
    warnings: List[Dict[str, Any]] = Field(default_factory=list, description="Validation warnings")


class SubmitStepDataResponse(BaseModel):
    """Response for step data submission."""
    
    success: bool = Field(..., description="Whether submission was successful")
    validation_result: ValidationResult = Field(..., description="Validation results")
    next_step: Optional[OnboardingStep] = Field(None, description="Next step configuration")
    progress_percentage: int = Field(..., description="Overall progress percentage")
    can_proceed: bool = Field(..., description="Whether user can proceed to next step")


class OnboardingFlowConfig(BaseModel):
    """Onboarding flow configuration."""
    
    steps: List[OnboardingStep] = Field(..., description="Available steps")
    service_type: ServiceType = Field(..., description="Service type")
    total_steps: int = Field(..., description="Total number of steps")
    current_step: int = Field(..., description="Current step number")
    progress: int = Field(..., description="Progress percentage (0-100)")
    can_go_back: bool = Field(..., description="Whether back navigation is allowed")
    can_go_next: bool = Field(..., description="Whether next navigation is allowed")
    can_skip: bool = Field(..., description="Whether current step can be skipped")


class OnboardingFlowState(BaseModel):
    """Current onboarding flow state."""
    
    session_id: str = Field(..., description="Session identifier")
    submission_id: Optional[str] = Field(None, description="Submission identifier")
    current_step: int = Field(..., description="Current step number")
    current_step_name: StepName = Field(..., description="Current step name")
    step_history: List[str] = Field(..., description="Completed step IDs")
    form_data: Dict[str, Any] = Field(..., description="Accumulated form data")
    service_type: ServiceType = Field(..., description="Selected service type")
    is_complete: bool = Field(..., description="Whether flow is complete")
    started_at: datetime = Field(..., description="When flow started")
    last_active_at: datetime = Field(..., description="Last activity timestamp")


class StartOnboardingFlowResponse(BaseModel):
    """Response for starting onboarding flow."""
    
    session_id: str = Field(..., description="Session identifier")
    flow_config: OnboardingFlowConfig = Field(..., description="Flow configuration")
    current_step: OnboardingStep = Field(..., description="First step to display")
    analytics_id: str = Field(..., description="Analytics tracking ID")


# ============================================================================
# BETTER AUTH USER SCHEMAS
# ============================================================================

class UserBase(BaseModel):
    """Base user schema for Better Auth."""
    
    name: Optional[str] = Field(None, description="User's display name")
    email: str = Field(..., description="User's email address")
    role: UserRole = Field(UserRole.ADMIN, description="User role")
    
    @validator('email')
    def validate_email(cls, v):
        """Validate email format."""
        import re
        if not re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$', v):
            raise ValueError('Invalid email format')
        return v.lower()


class UserCreate(UserBase):
    """Schema for creating a new user."""
    
    emailVerified: bool = Field(False, description="Whether email is verified")
    image: Optional[str] = Field(None, description="Profile image URL")


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    
    name: Optional[str] = Field(None, description="User's display name")
    email: Optional[str] = Field(None, description="User's email address")
    emailVerified: Optional[bool] = Field(None, description="Whether email is verified")
    image: Optional[str] = Field(None, description="Profile image URL")
    role: Optional[UserRole] = Field(None, description="User role")
    
    @validator('email')
    def validate_email(cls, v):
        """Validate email format."""
        if v is not None:
            import re
            if not re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$', v):
                raise ValueError('Invalid email format')
            return v.lower()
        return v


class User(BaseSchema):
    """User response schema."""
    
    name: Optional[str] = Field(None, description="User's display name")
    email: str = Field(..., description="User's email address")
    emailVerified: bool = Field(..., description="Whether email is verified")
    image: Optional[str] = Field(None, description="Profile image URL")
    role: UserRole = Field(..., description="User role")


class UserList(BaseModel):
    """Schema for listing users with filters."""
    
    role: Optional[UserRole] = Field(None, description="Filter by role")
    emailVerified: Optional[bool] = Field(None, description="Filter by email verification status")
    search: Optional[str] = Field(None, description="Search by name or email")


# Better Auth Session Schemas
class SessionBase(BaseModel):
    """Base session schema."""
    
    userId: str = Field(..., description="User ID")
    token: str = Field(..., description="Session token")
    expiresAt: datetime = Field(..., description="Session expiration time")
    ipAddress: Optional[str] = Field(None, description="Client IP address")
    userAgent: Optional[str] = Field(None, description="Client user agent")


class SessionCreate(SessionBase):
    """Schema for creating a session."""
    pass


class Session(BaseSchema):
    """Session response schema."""
    
    userId: str = Field(..., description="User ID")
    token: str = Field(..., description="Session token")
    expiresAt: datetime = Field(..., description="Session expiration time")
    ipAddress: Optional[str] = Field(None, description="Client IP address")
    userAgent: Optional[str] = Field(None, description="Client user agent")
    
    # Add user information for convenience
    user: Optional[User] = Field(None, description="Associated user information")


# Better Auth Account Schemas (OAuth)
class AccountBase(BaseModel):
    """Base account schema for OAuth providers."""
    
    userId: str = Field(..., description="User ID")
    providerId: OAuthProvider = Field(..., description="OAuth provider")
    accountId: str = Field(..., description="Provider-specific account ID")
    accessToken: Optional[str] = Field(None, description="OAuth access token")
    refreshToken: Optional[str] = Field(None, description="OAuth refresh token")
    expiresAt: Optional[datetime] = Field(None, description="Token expiration time")
    scope: Optional[str] = Field(None, description="OAuth scope")
    tokenType: str = Field("bearer", description="Token type")


class AccountCreate(AccountBase):
    """Schema for creating an OAuth account link."""
    pass


class AccountUpdate(BaseModel):
    """Schema for updating OAuth account information."""
    
    accessToken: Optional[str] = Field(None, description="OAuth access token")
    refreshToken: Optional[str] = Field(None, description="OAuth refresh token")
    expiresAt: Optional[datetime] = Field(None, description="Token expiration time")
    scope: Optional[str] = Field(None, description="OAuth scope")


class Account(BaseSchema):
    """Account response schema."""
    
    userId: str = Field(..., description="User ID")
    providerId: OAuthProvider = Field(..., description="OAuth provider")
    accountId: str = Field(..., description="Provider-specific account ID")
    expiresAt: Optional[datetime] = Field(None, description="Token expiration time")
    scope: Optional[str] = Field(None, description="OAuth scope")
    tokenType: str = Field(..., description="Token type")
    
    # Add user information for convenience
    user: Optional[User] = Field(None, description="Associated user information")
    
    # Note: We don't expose tokens in responses for security


# Authentication Request/Response Schemas
class LoginRequest(BaseModel):
    """Login request schema."""
    
    email: str = Field(..., description="User email")
    password: str = Field(..., description="User password")
    remember_me: bool = Field(False, description="Remember login")


class LoginResponse(BaseModel):
    """Login response schema."""
    
    user: User = Field(..., description="User information")
    session: Session = Field(..., description="Session information")
    access_token: str = Field(..., description="Access token")
    token_type: str = Field("bearer", description="Token type")


class RegisterRequest(BaseModel):
    """Registration request schema."""
    
    name: Optional[str] = Field(None, description="User's display name")
    email: str = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")
    
    @validator('email')
    def validate_email(cls, v):
        """Validate email format."""
        import re
        if not re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$', v):
            raise ValueError('Invalid email format')
        return v.lower()
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class PasswordChangeRequest(BaseModel):
    """Password change request schema."""
    
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., description="New password")
    
    @validator('new_password')
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class EmailVerificationRequest(BaseModel):
    """Email verification request schema."""
    
    email: str = Field(..., description="Email to verify")
    
    @validator('email')
    def validate_email(cls, v):
        """Validate email format."""
        import re
        if not re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$', v):
            raise ValueError('Invalid email format')
        return v.lower()


class PasswordResetRequest(BaseModel):
    """Password reset request schema."""
    
    email: str = Field(..., description="Email for password reset")
    
    @validator('email')
    def validate_email(cls, v):
        """Validate email format."""
        import re
        if not re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$', v):
            raise ValueError('Invalid email format')
        return v.lower()
