"""
Database migration utilities for PostgreSQL.
"""

import logging
import asyncio
from typing import Dict, Any, List

from app.database.postgres import db_manager, get_db_session
from app.models.database import (
    PricingPlan, Feature, ProcessStep, HeroSection, Testimonial,
    ContactInfo, FAQ, SiteSetting, AddonService,
    PlanCategory, ButtonVariant, ContactType, FAQCategory,
    SettingType, ServiceCategory, ProjectType, ServiceUnit
)

logger = logging.getLogger(__name__)


class DatabaseMigration:
    """Database migration manager."""
    
    async def initialize_tables(self):
        """Create all database tables."""
        try:
            await db_manager.initialize()
            await db_manager.create_tables()
            logger.info("✅ Database tables created successfully")
        except Exception as e:
            logger.error(f"❌ Failed to create tables: {e}")
            raise
    
    async def seed_sample_data(self):
        """Seed database with sample data."""
        try:
            async with db_manager.get_session() as session:
                # Check if data already exists
                from sqlalchemy import select, func
                existing_plans = await session.execute(select(func.count(PricingPlan.id)))
                count = existing_plans.scalar()
                
                if count > 0:
                    logger.info("Database already contains data, skipping seed")
                    return
                
                # Sample pricing plans
                sample_plans = [
                    PricingPlan(
                        plan_id="basic-web",
                        name="Basic Website",
                        price="$299",
                        period="one-time",
                        description="Perfect for small businesses and personal websites",
                        features=["1-3 Pages", "Mobile Responsive", "Basic SEO", "Contact Form"],
                        button_text="Get Started",
                        button_variant=ButtonVariant.OUTLINE,
                        popular=False,
                        timeline="1-2 weeks",
                        display_order=1,
                        category=PlanCategory.WEB,
                        is_active=True
                    ),
                    PricingPlan(
                        plan_id="premium-web",
                        name="Premium Website",
                        price="$599",
                        period="one-time",
                        description="Ideal for growing businesses with advanced features",
                        features=["5-10 Pages", "Mobile Responsive", "Advanced SEO", "CMS Integration", "Analytics Setup"],
                        button_text="Choose Premium",
                        button_variant=ButtonVariant.DEFAULT,
                        popular=True,
                        timeline="2-3 weeks",
                        display_order=2,
                        category=PlanCategory.WEB,
                        is_active=True
                    ),
                    PricingPlan(
                        plan_id="mobile-app",
                        name="Mobile App",
                        price="$1,999",
                        period="one-time",
                        description="Custom mobile app for iOS and Android",
                        features=["Cross-Platform", "Custom Design", "API Integration", "App Store Submission"],
                        button_text="Start Project",
                        button_variant=ButtonVariant.DEFAULT,
                        popular=False,
                        timeline="4-6 weeks",
                        display_order=3,
                        category=PlanCategory.MOBILE,
                        is_active=True
                    )
                ]
                
                # Sample features
                sample_features = [
                    Feature(
                        title="Responsive Design",
                        description="Your website will look perfect on all devices",
                        icon="Smartphone",
                        color="from-blue-500 to-blue-600",
                        display_order=1,
                        is_active=True
                    ),
                    Feature(
                        title="SEO Optimized",
                        description="Built-in SEO best practices to help you rank higher",
                        icon="Search",
                        color="from-green-500 to-green-600",
                        display_order=2,
                        is_active=True
                    ),
                    Feature(
                        title="Fast Loading",
                        description="Optimized for speed and performance",
                        icon="Zap",
                        color="from-yellow-500 to-yellow-600",
                        display_order=3,
                        is_active=True
                    )
                ]
                
                # Sample process steps
                sample_steps = [
                    ProcessStep(
                        step_number=1,
                        title="Discovery & Planning",
                        description="We start by understanding your goals and requirements",
                        icon="Search",
                        details=["Requirements gathering", "Project scope definition", "Timeline planning"],
                        display_order=1,
                        is_active=True
                    ),
                    ProcessStep(
                        step_number=2,
                        title="Design & Development",
                        description="Creating your custom solution",
                        icon="Code",
                        details=["UI/UX design", "Development", "Testing"],
                        display_order=2,
                        is_active=True
                    ),
                    ProcessStep(
                        step_number=3,
                        title="Launch & Support",
                        description="Going live and ongoing maintenance",
                        icon="Rocket",
                        details=["Deployment", "Training", "Ongoing support"],
                        display_order=3,
                        is_active=True
                    )
                ]
                
                # Sample hero section
                sample_hero = HeroSection(
                    headline="Transform Your Digital Presence",
                    subheadline="Professional web development and mobile app solutions tailored to your business needs",
                    cta_text="Get Started",
                    cta_variant=ButtonVariant.DEFAULT,
                    secondary_cta_text="View Portfolio",
                    secondary_cta_variant=ButtonVariant.OUTLINE,
                    background_video=None,
                    is_active=True
                )
                
                # Sample testimonial
                sample_testimonial = Testimonial(
                    client_name="John Smith",
                    client_company="Tech Startup Inc.",
                    client_role="CEO",
                    testimonial="Lunaxcode delivered exactly what we needed. Professional, fast, and high-quality work.",
                    rating=5,
                    avatar=None,
                    project_type=ProjectType.WEB_APP,
                    display_order=1,
                    is_active=True
                )
                
                # Sample contact info
                sample_contacts = [
                    ContactInfo(
                        type=ContactType.EMAIL,
                        label="Email",
                        value="hello@lunaxcode.com",
                        icon="Mail",
                        is_primary=True,
                        display_order=1,
                        is_active=True
                    ),
                    ContactInfo(
                        type=ContactType.PHONE,
                        label="Phone",
                        value="+1 (555) 123-4567",
                        icon="Phone",
                        is_primary=False,
                        display_order=2,
                        is_active=True
                    )
                ]
                
                # Sample FAQ
                sample_faq = FAQ(
                    question="What's included in the basic package?",
                    answer="The basic package includes up to 3 pages, mobile responsive design, basic SEO optimization, and a contact form.",
                    category=FAQCategory.PRICING,
                    display_order=1,
                    is_active=True
                )
                
                # Sample site settings
                sample_settings = [
                    SiteSetting(
                        key="site_name",
                        value="Lunaxcode",
                        type=SettingType.TEXT,
                        description="Website name",
                        is_public=True
                    ),
                    SiteSetting(
                        key="contact_email",
                        value="hello@lunaxcode.com",
                        type=SettingType.TEXT,
                        description="Primary contact email",
                        is_public=True
                    )
                ]
                
                # Sample addon service
                sample_addon = AddonService(
                    service_id="seo-boost",
                    name="SEO Optimization",
                    price="$199",
                    description="Advanced SEO optimization to improve search rankings",
                    unit=ServiceUnit.ONE_TIME,
                    category=ServiceCategory.SEO,
                    icon="TrendingUp",
                    popular=True,
                    display_order=1,
                    is_active=True
                )
                
                # Add all sample data
                all_items = (
                    sample_plans + sample_features + sample_steps + 
                    [sample_hero, sample_testimonial] + sample_contacts + 
                    [sample_faq] + sample_settings + [sample_addon]
                )
                
                for item in all_items:
                    session.add(item)
                
                await session.commit()
                logger.info("✅ Sample data seeded successfully")
                
        except Exception as e:
            logger.error(f"❌ Failed to seed sample data: {e}")
            raise
    
    async def run_migration(self):
        """Run full migration: create tables and seed data."""
        logger.info("Starting database migration...")
        
        await self.initialize_tables()
        await self.seed_sample_data()
        
        logger.info("✅ Database migration completed successfully")


async def migrate():
    """Run database migration."""
    migration = DatabaseMigration()
    await migration.run_migration()


if __name__ == "__main__":
    asyncio.run(migrate())
