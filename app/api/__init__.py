"""
API router configuration.
"""

from fastapi import APIRouter

from app.api.v1 import (
    auth, pricing_plans, features, process_steps, hero_section, 
    testimonials, contact_info, faqs, site_settings, addon_services,
    onboarding, users
)

api_router = APIRouter()

# Include authentication router
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Include all content endpoint routers
api_router.include_router(pricing_plans.router, prefix="/pricing-plans", tags=["Pricing Plans"])
api_router.include_router(features.router, prefix="/features", tags=["Features"])
api_router.include_router(process_steps.router, prefix="/process-steps", tags=["Process Steps"])
api_router.include_router(hero_section.router, prefix="/hero-section", tags=["Hero Section"])
api_router.include_router(testimonials.router, prefix="/testimonials", tags=["Testimonials"])
api_router.include_router(contact_info.router, prefix="/contact-info", tags=["Contact Info"])
api_router.include_router(faqs.router, prefix="/faqs", tags=["FAQs"])
api_router.include_router(site_settings.router, prefix="/site-settings", tags=["Site Settings"])
api_router.include_router(addon_services.router, prefix="/addon-services", tags=["Addon Services"])
api_router.include_router(onboarding.router, prefix="/onboarding", tags=["Onboarding"])
api_router.include_router(users.router, prefix="/users", tags=["Better Auth - Users"])
