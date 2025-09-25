#!/usr/bin/env python3
"""
Seed data script for Lunaxcode CMS Admin API.
Creates realistic sample data for all content tables.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database.xata import get_database
from app.services.base import BaseService
from app.services.pricing_plans import PricingPlansService
from app.models.content import (
    PricingPlanCreate, PricingPlan, PlanCategory, ButtonVariant,
    FeatureCreate, Feature, FeatureUpdate,
    ProcessStepCreate, ProcessStep, ProcessStepUpdate,
    HeroSectionCreate, HeroSection, HeroSectionUpdate,
    TestimonialCreate, Testimonial, TestimonialUpdate, ProjectType,
    ContactInfoCreate, ContactInfo, ContactInfoUpdate, ContactType,
    FAQCreate, FAQ, FAQUpdate, FAQCategory,
    SiteSettingCreate, SiteSetting, SiteSettingUpdate, SettingType,
    AddonServiceCreate, AddonService, AddonServiceUpdate, ServiceCategory, ServiceUnit
)


class SeedData:
    """Seed data manager for all content tables."""
    
    def __init__(self):
        self.db = None
    
    async def connect(self):
        """Initialize database connection."""
        self.db = await get_database()
        await self.db.connect()
        print("✅ Connected to Xata database")
    
    async def clear_all_tables(self):
        """Clear all existing data from tables."""
        print("⚠️ Skipping table clearing - will create new records alongside existing ones")
        print("   Note: To clear tables, use the API endpoints or Xata dashboard")
    
    async def seed_pricing_plans(self):
        """Seed pricing plans data."""
        plans = [
            PricingPlanCreate(
                planId="landing_basic",
                name="Landing Page Basic",
                price="₱9,999",
                period="one-time",
                description="Perfect for small businesses needing a professional online presence",
                features=[
                    "Custom design",
                    "Mobile responsive",
                    "Contact form",
                    "SEO optimized",
                    "48-hour delivery"
                ],
                buttonText="Get Started",
                buttonVariant=ButtonVariant.OUTLINE,
                popular=False,
                timeline="48 hours",
                displayOrder=1,
                category=PlanCategory.WEB,
                isActive=True
            ),
            PricingPlanCreate(
                planId="landing_premium",
                name="Landing Page Premium",
                price="₱19,999",
                period="one-time",
                description="Enhanced landing page with advanced features and integrations",
                features=[
                    "Premium custom design",
                    "Mobile responsive",
                    "Contact form with validation",
                    "Advanced SEO optimization",
                    "Social media integration",
                    "Analytics setup",
                    "24-hour delivery"
                ],
                buttonText="Choose Premium",
                buttonVariant=ButtonVariant.DEFAULT,
                popular=True,
                timeline="24 hours",
                displayOrder=2,
                category=PlanCategory.WEB,
                isActive=True
            ),
            PricingPlanCreate(
                planId="webapp_starter",
                name="Web App Starter",
                price="₱49,999",
                period="one-time",
                description="Complete web application with user authentication and basic features",
                features=[
                    "Custom web application",
                    "User authentication",
                    "Database integration",
                    "Admin dashboard",
                    "Mobile responsive design",
                    "API development",
                    "7-day delivery"
                ],
                buttonText="Start Building",
                buttonVariant=ButtonVariant.OUTLINE,
                popular=False,
                timeline="7 days",
                displayOrder=3,
                category=PlanCategory.WEB,
                isActive=True
            ),
            PricingPlanCreate(
                planId="webapp_professional",
                name="Web App Professional",
                price="₱99,999",
                period="one-time",
                description="Advanced web application with complex features and integrations",
                features=[
                    "Advanced web application",
                    "Multi-user authentication",
                    "Complex database design",
                    "Advanced admin panel",
                    "Payment integration",
                    "Email automation",
                    "API with documentation",
                    "14-day delivery"
                ],
                buttonText="Go Professional",
                buttonVariant=ButtonVariant.DEFAULT,
                popular=True,
                timeline="14 days",
                displayOrder=4,
                category=PlanCategory.WEB,
                isActive=True
            ),
            PricingPlanCreate(
                planId="mobile_basic",
                name="Mobile App Basic",
                price="₱79,999",
                period="one-time",
                description="Simple mobile application for iOS and Android platforms",
                features=[
                    "Cross-platform mobile app",
                    "iOS & Android compatible",
                    "Basic user interface",
                    "Local data storage",
                    "Push notifications",
                    "21-day delivery"
                ],
                buttonText="Build Mobile",
                buttonVariant=ButtonVariant.OUTLINE,
                popular=False,
                timeline="21 days",
                displayOrder=5,
                category=PlanCategory.MOBILE,
                isActive=True
            ),
            PricingPlanCreate(
                planId="mobile_advanced",
                name="Mobile App Advanced",
                price="₱149,999",
                period="one-time",
                description="Feature-rich mobile application with backend integration",
                features=[
                    "Advanced mobile application",
                    "iOS & Android compatible",
                    "Backend API integration",
                    "User authentication",
                    "Real-time features",
                    "Push notifications",
                    "App store deployment",
                    "30-day delivery"
                ],
                buttonText="Advanced Mobile",
                buttonVariant=ButtonVariant.DEFAULT,
                popular=True,
                timeline="30 days",
                displayOrder=6,
                category=PlanCategory.MOBILE,
                isActive=True
            ),
            PricingPlanCreate(
                planId="ecommerce_basic",
                name="E-commerce Basic",
                price="₱39,999",
                period="one-time",
                description="Complete online store with payment processing",
                features=[
                    "Custom e-commerce website",
                    "Product catalog",
                    "Shopping cart",
                    "Payment gateway integration",
                    "Order management",
                    "Mobile responsive",
                    "10-day delivery"
                ],
                buttonText="Start Selling",
                buttonVariant=ButtonVariant.OUTLINE,
                popular=False,
                timeline="10 days",
                displayOrder=7,
                category=PlanCategory.WEB,
                isActive=True
            ),
            PricingPlanCreate(
                planId="ecommerce_pro",
                name="E-commerce Professional",
                price="₱69,999",
                period="one-time",
                description="Advanced e-commerce platform with analytics and marketing tools",
                features=[
                    "Advanced e-commerce platform",
                    "Multi-vendor support",
                    "Advanced analytics",
                    "Email marketing integration",
                    "Inventory management",
                    "Customer reviews",
                    "SEO optimization",
                    "Admin dashboard",
                    "14-day delivery"
                ],
                buttonText="Scale Business",
                buttonVariant=ButtonVariant.DEFAULT,
                popular=True,
                timeline="14 days",
                displayOrder=8,
                category=PlanCategory.WEB,
                isActive=True
            ),
            PricingPlanCreate(
                planId="consulting",
                name="Development Consulting",
                price="₱2,500",
                period="per hour",
                description="Expert development consultation and code review services",
                features=[
                    "Technical consultation",
                    "Code review",
                    "Architecture planning",
                    "Performance optimization",
                    "Security audit",
                    "Best practices guidance"
                ],
                buttonText="Book Consultation",
                buttonVariant=ButtonVariant.SECONDARY,
                popular=False,
                timeline="Same day",
                displayOrder=9,
                category=PlanCategory.WEB,
                isActive=True
            ),
            PricingPlanCreate(
                planId="maintenance",
                name="Website Maintenance",
                price="₱4,999",
                period="per month",
                description="Ongoing website maintenance and support services",
                features=[
                    "Regular updates",
                    "Security monitoring",
                    "Performance optimization",
                    "Content updates",
                    "Technical support",
                    "Monthly reports"
                ],
                buttonText="Subscribe",
                buttonVariant=ButtonVariant.OUTLINE,
                popular=False,
                timeline="Ongoing",
                displayOrder=10,
                category=PlanCategory.WEB,
                isActive=True
            )
        ]
        
        # Use the pricing plans service
        service = PricingPlansService(self.db)
        for plan in plans:
            try:
                await service.create(plan)
                print(f"  ✅ Created: {plan.name}")
            except Exception as e:
                print(f"  ❌ Failed to create {plan.name}: {e}")
        
        print(f"✅ Seeded {len(plans)} pricing plans")
    
    async def seed_features(self):
        """Seed features data."""
        features = [
            FeatureCreate(
                title="Lightning Fast Development",
                description="Get your project up and running in record time with our streamlined development process and proven frameworks.",
                icon="Zap",
                color="from-yellow-400 to-orange-500",
                displayOrder=1,
                isActive=True
            ),
            FeatureCreate(
                title="Mobile-First Design",
                description="Every project is built with mobile users in mind, ensuring perfect functionality across all devices and screen sizes.",
                icon="Smartphone",
                color="from-blue-400 to-purple-500",
                displayOrder=2,
                isActive=True
            ),
            FeatureCreate(
                title="SEO Optimized",
                description="Built-in SEO best practices to help your website rank higher in search results and attract more organic traffic.",
                icon="Search",
                color="from-green-400 to-blue-500",
                displayOrder=3,
                isActive=True
            ),
            FeatureCreate(
                title="Secure & Reliable",
                description="Enterprise-grade security measures and reliable hosting ensure your application is always safe and accessible.",
                icon="Shield",
                color="from-red-400 to-pink-500",
                displayOrder=4,
                isActive=True
            ),
            FeatureCreate(
                title="Custom Integrations",
                description="Seamlessly integrate with your existing tools and services including payment gateways, CRMs, and analytics platforms.",
                icon="Puzzle",
                color="from-purple-400 to-indigo-500",
                displayOrder=5,
                isActive=True
            ),
            FeatureCreate(
                title="24/7 Support",
                description="Round-the-clock technical support to ensure your application runs smoothly and any issues are resolved quickly.",
                icon="HeadphonesIcon",
                color="from-teal-400 to-green-500",
                displayOrder=6,
                isActive=True
            ),
            FeatureCreate(
                title="Scalable Architecture",
                description="Built to grow with your business, our applications can handle increased traffic and feature additions effortlessly.",
                icon="TrendingUp",
                color="from-indigo-400 to-purple-500",
                displayOrder=7,
                isActive=True
            ),
            FeatureCreate(
                title="Modern Tech Stack",
                description="Utilizing the latest technologies and frameworks to ensure your application is future-proof and maintainable.",
                icon="Code",
                color="from-gray-400 to-gray-600",
                displayOrder=8,
                isActive=True
            ),
            FeatureCreate(
                title="Analytics & Insights",
                description="Comprehensive analytics setup to track user behavior, performance metrics, and business growth indicators.",
                icon="BarChart3",
                color="from-orange-400 to-red-500",
                displayOrder=9,
                isActive=True
            ),
            FeatureCreate(
                title="Cloud Deployment",
                description="Professional deployment on reliable cloud platforms with automatic backups and monitoring included.",
                icon="Cloud",
                color="from-cyan-400 to-blue-500",
                displayOrder=10,
                isActive=True
            )
        ]
        
        # Use the base service for features
        service = BaseService(
            db=self.db,
            table_name="features",
            model_class=Feature,
            create_model_class=FeatureCreate,
            update_model_class=FeatureUpdate
        )
        for feature in features:
            try:
                await service.create(feature)
                print(f"  ✅ Created: {feature.title}")
            except Exception as e:
                print(f"  ❌ Failed to create {feature.title}: {e}")
        
        print(f"✅ Seeded {len(features)} features")
    
    async def seed_process_steps(self):
        """Seed process steps data."""
        steps = [
            ProcessStepCreate(
                stepNumber=1,
                title="Discovery & Planning",
                description="We start by understanding your business goals, target audience, and project requirements to create a comprehensive development plan.",
                icon="Search",
                details=[
                    "Detailed requirement analysis",
                    "Target audience research",
                    "Competitive analysis",
                    "Technology stack selection",
                    "Project timeline planning"
                ],
                displayOrder=1,
                isActive=True
            ),
            ProcessStepCreate(
                stepNumber=2,
                title="Design & Prototyping",
                description="Create wireframes, mockups, and interactive prototypes to visualize the final product before development begins.",
                icon="Palette",
                details=[
                    "User experience design",
                    "Visual interface mockups",
                    "Interactive prototypes",
                    "Design system creation",
                    "Client feedback integration"
                ],
                displayOrder=2,
                isActive=True
            ),
            ProcessStepCreate(
                stepNumber=3,
                title="Development",
                description="Our expert developers bring your vision to life using modern technologies and industry best practices.",
                icon="Code",
                details=[
                    "Frontend development",
                    "Backend API creation",
                    "Database design and setup",
                    "Third-party integrations",
                    "Quality assurance testing"
                ],
                displayOrder=3,
                isActive=True
            ),
            ProcessStepCreate(
                stepNumber=4,
                title="Testing & Quality Assurance",
                description="Comprehensive testing across all devices and browsers to ensure flawless functionality and user experience.",
                icon="CheckCircle",
                details=[
                    "Cross-browser testing",
                    "Mobile responsiveness testing",
                    "Performance optimization",
                    "Security vulnerability scanning",
                    "User acceptance testing"
                ],
                displayOrder=4,
                isActive=True
            ),
            ProcessStepCreate(
                stepNumber=5,
                title="Deployment & Launch",
                description="Deploy your application to production servers with proper configuration, monitoring, and security measures.",
                icon="Rocket",
                details=[
                    "Production server setup",
                    "Domain and SSL configuration",
                    "Database migration",
                    "Performance monitoring",
                    "Launch coordination"
                ],
                displayOrder=5,
                isActive=True
            ),
            ProcessStepCreate(
                stepNumber=6,
                title="Training & Documentation",
                description="Provide comprehensive training and documentation to ensure you can manage and update your application effectively.",
                icon="BookOpen",
                details=[
                    "Admin panel training",
                    "Content management guidance",
                    "Technical documentation",
                    "Best practices guide",
                    "Video tutorials"
                ],
                displayOrder=6,
                isActive=True
            ),
            ProcessStepCreate(
                stepNumber=7,
                title="Ongoing Support",
                description="Continuous support and maintenance to keep your application running smoothly and up-to-date.",
                icon="HeadphonesIcon",
                details=[
                    "Technical support",
                    "Regular updates",
                    "Security monitoring",
                    "Performance optimization",
                    "Feature enhancements"
                ],
                displayOrder=7,
                isActive=True
            ),
            ProcessStepCreate(
                stepNumber=8,
                title="Analytics & Optimization",
                description="Monitor performance metrics and user behavior to continuously improve and optimize your application.",
                icon="BarChart3",
                details=[
                    "Performance analytics setup",
                    "User behavior tracking",
                    "Conversion optimization",
                    "A/B testing implementation",
                    "Monthly performance reports"
                ],
                displayOrder=8,
                isActive=True
            ),
            ProcessStepCreate(
                stepNumber=9,
                title="Scaling & Growth",
                description="Plan and implement scaling strategies as your business grows and requires additional features or capacity.",
                icon="TrendingUp",
                details=[
                    "Infrastructure scaling",
                    "Feature expansion planning",
                    "Performance optimization",
                    "Team collaboration setup",
                    "Long-term roadmap development"
                ],
                displayOrder=9,
                isActive=True
            ),
            ProcessStepCreate(
                stepNumber=10,
                title="Success Measurement",
                description="Evaluate project success through key metrics, user feedback, and business goal achievement.",
                icon="Target",
                details=[
                    "ROI measurement",
                    "User satisfaction surveys",
                    "Business goal tracking",
                    "Performance benchmarking",
                    "Success story documentation"
                ],
                displayOrder=10,
                isActive=True
            )
        ]
        
        # Use the base service for process steps
        service = BaseService(
            db=self.db,
            table_name="process_steps", 
            model_class=ProcessStep,
            create_model_class=ProcessStepCreate,
            update_model_class=ProcessStepUpdate
        )
        for step in steps:
            try:
                await service.create(step)
                print(f"  ✅ Created: {step.title}")
            except Exception as e:
                print(f"  ❌ Failed to create {step.title}: {e}")
        
        print(f"✅ Seeded {len(steps)} process steps")
    
    async def seed_hero_sections(self):
        """Seed hero section data."""
        sections = [
            HeroSectionCreate(
                headline="Build Your Digital Future with Expert Development",
                subheadline="From landing pages to complex web applications, we create digital solutions that drive your business forward. Fast, reliable, and tailored to your needs.",
                ctaText="Start Your Project",
                ctaVariant=ButtonVariant.DEFAULT,
                secondaryCtaText="View Our Work",
                secondaryCtaVariant=ButtonVariant.OUTLINE,
                backgroundVideo=None,
                isActive=True
            ),
            HeroSectionCreate(
                headline="Transform Ideas Into Powerful Digital Solutions",
                subheadline="Professional web and mobile app development services that help businesses grow online. Modern technology, proven results.",
                ctaText="Get Started Today",
                ctaVariant=ButtonVariant.DEFAULT,
                secondaryCtaText="Learn More",
                secondaryCtaVariant=ButtonVariant.OUTLINE,
                backgroundVideo=None,
                isActive=False
            ),
            HeroSectionCreate(
                headline="Your Vision, Our Code, Amazing Results",
                subheadline="Custom development solutions built with cutting-edge technology. From concept to deployment, we handle everything so you can focus on growing your business.",
                ctaText="Build With Us",
                ctaVariant=ButtonVariant.DEFAULT,
                secondaryCtaText="See Pricing",
                secondaryCtaVariant=ButtonVariant.OUTLINE,
                backgroundVideo=None,
                isActive=False
            )
        ]
        
        # Use the base service for hero sections
        service = BaseService(
            db=self.db,
            table_name="hero_sections",
            model_class=HeroSection,
            create_model_class=HeroSectionCreate,
            update_model_class=HeroSectionUpdate
        )
        for section in sections:
            try:
                await service.create(section)
                print(f"  ✅ Created: {section.headline[:50]}...")
            except Exception as e:
                print(f"  ❌ Failed to create hero section: {e}")
        
        print(f"✅ Seeded {len(sections)} hero sections")
    
    async def seed_testimonials(self):
        """Seed testimonials data."""
        testimonials = [
            TestimonialCreate(
                clientName="Maria Santos",
                clientCompany="Santos Bakery",
                clientRole="Owner",
                testimonial="The landing page they created for our bakery increased our online orders by 200%. The design is beautiful and works perfectly on mobile. Highly recommend!",
                rating=5,
                avatar="https://images.unsplash.com/photo-1494790108755-2616b612b789?w=150",
                projectType=ProjectType.LANDING_PAGE,
                displayOrder=1,
                isActive=True
            ),
            TestimonialCreate(
                clientName="Carlos Rodriguez",
                clientCompany="TechStart Solutions",
                clientRole="CEO",
                testimonial="Our web application was delivered on time and exceeded expectations. The team's attention to detail and communication throughout the project was exceptional.",
                rating=5,
                avatar="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150",
                projectType=ProjectType.WEB_APP,
                displayOrder=2,
                isActive=True
            ),
            TestimonialCreate(
                clientName="Ana Dela Cruz",
                clientCompany="Fitness Plus Gym",
                clientRole="Marketing Manager",
                testimonial="The mobile app they developed for our gym has been a game-changer. Members love the booking system and workout tracking features. Great work!",
                rating=5,
                avatar="https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150",
                projectType=ProjectType.MOBILE_APP,
                displayOrder=3,
                isActive=True
            ),
            TestimonialCreate(
                clientName="Roberto Chen",
                clientCompany="Chen Electronics",
                clientRole="Store Manager",
                testimonial="Our e-commerce website looks professional and works flawlessly. Sales have increased significantly since the launch. Thank you for the excellent service!",
                rating=5,
                avatar="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150",
                projectType=ProjectType.WEB_APP,
                displayOrder=4,
                isActive=True
            ),
            TestimonialCreate(
                clientName="Isabella Reyes",
                clientCompany="Reyes Consulting",
                clientRole="Principal Consultant",
                testimonial="Professional, efficient, and results-driven. The landing page perfectly represents our brand and has generated quality leads from day one.",
                rating=5,
                avatar="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150",
                projectType=ProjectType.LANDING_PAGE,
                displayOrder=5,
                isActive=True
            ),
            TestimonialCreate(
                clientName="Miguel Torres",
                clientCompany="Torres Construction",
                clientRole="Project Manager",
                testimonial="The project management app they built streamlined our operations completely. We can now track projects in real-time and our efficiency has improved by 40%.",
                rating=5,
                avatar="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150",
                projectType=ProjectType.WEB_APP,
                displayOrder=6,
                isActive=True
            ),
            TestimonialCreate(
                clientName="Sofia Gutierrez",
                clientCompany="Bloom Flower Shop",
                clientRole="Owner",
                testimonial="Beautiful website design and smooth ordering system. Our customers frequently compliment the user experience. Couldn't be happier with the results!",
                rating=5,
                avatar="https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150",
                projectType=ProjectType.LANDING_PAGE,
                displayOrder=7,
                isActive=True
            ),
            TestimonialCreate(
                clientName="David Park",
                clientCompany="Park Medical Clinic",
                clientRole="Practice Administrator",
                testimonial="The appointment booking system has revolutionized how we manage patient schedules. Both staff and patients love how easy it is to use.",
                rating=5,
                avatar="https://images.unsplash.com/photo-1560250097-0b93528c311a?w=150",
                projectType=ProjectType.WEB_APP,
                displayOrder=8,
                isActive=True
            ),
            TestimonialCreate(
                clientName="Carmen Lopez",
                clientCompany="Lopez Travel Agency",
                clientRole="Travel Consultant",
                testimonial="Our new booking platform has automated so many manual processes. We can now serve more clients while providing better service. Fantastic investment!",
                rating=5,
                avatar="https://images.unsplash.com/photo-1489424731084-a5d8b219a5bb?w=150",
                projectType=ProjectType.WEB_APP,
                displayOrder=9,
                isActive=True
            ),
            TestimonialCreate(
                clientName="Luis Fernandez",
                clientCompany="Fernandez Auto Shop",
                clientRole="Owner",
                testimonial="The mobile app for our auto shop allows customers to book services and track repairs. It's professional, user-friendly, and has improved customer satisfaction significantly.",
                rating=5,
                avatar="https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=150",
                projectType=ProjectType.MOBILE_APP,
                displayOrder=10,
                isActive=True
            )
        ]
        
        # Use the base service for testimonials
        service = BaseService(
            db=self.db,
            table_name="testimonials",
            model_class=Testimonial,
            create_model_class=TestimonialCreate,
            update_model_class=TestimonialUpdate
        )
        for testimonial in testimonials:
            try:
                await service.create(testimonial)
                print(f"  ✅ Created: {testimonial.clientName}")
            except Exception as e:
                print(f"  ❌ Failed to create {testimonial.clientName}: {e}")
        
        print(f"✅ Seeded {len(testimonials)} testimonials")
    
    async def seed_contact_info(self):
        """Seed contact info data."""
        contacts = [
            ContactInfoCreate(
                type=ContactType.EMAIL,
                label="Business Email",
                value="hello@lunaxcode.com",
                icon="Mail",
                isPrimary=True,
                displayOrder=1,
                isActive=True
            ),
            ContactInfoCreate(
                type=ContactType.EMAIL,
                label="Support Email",
                value="support@lunaxcode.com",
                icon="Mail",
                isPrimary=False,
                displayOrder=2,
                isActive=True
            ),
            ContactInfoCreate(
                type=ContactType.PHONE,
                label="Primary Phone",
                value="+63 917 123 4567",
                icon="Phone",
                isPrimary=True,
                displayOrder=3,
                isActive=True
            ),
            ContactInfoCreate(
                type=ContactType.PHONE,
                label="WhatsApp",
                value="+63 917 123 4567",
                icon="MessageCircle",
                isPrimary=False,
                displayOrder=4,
                isActive=True
            ),
            ContactInfoCreate(
                type=ContactType.ADDRESS,
                label="Business Address",
                value="123 Tech Hub, Makati City, Metro Manila, Philippines",
                icon="MapPin",
                isPrimary=True,
                displayOrder=5,
                isActive=True
            ),
            ContactInfoCreate(
                type=ContactType.SOCIAL,
                label="Facebook",
                value="https://facebook.com/lunaxcode",
                icon="Facebook",
                isPrimary=False,
                displayOrder=6,
                isActive=True
            ),
            ContactInfoCreate(
                type=ContactType.SOCIAL,
                label="Instagram",
                value="https://instagram.com/lunaxcode",
                icon="Instagram",
                isPrimary=False,
                displayOrder=7,
                isActive=True
            ),
            ContactInfoCreate(
                type=ContactType.SOCIAL,
                label="LinkedIn",
                value="https://linkedin.com/company/lunaxcode",
                icon="Linkedin",
                isPrimary=False,
                displayOrder=8,
                isActive=True
            ),
            ContactInfoCreate(
                type=ContactType.SOCIAL,
                label="Twitter",
                value="https://twitter.com/lunaxcode",
                icon="Twitter",
                isPrimary=False,
                displayOrder=9,
                isActive=True
            ),
            ContactInfoCreate(
                type=ContactType.EMAIL,
                label="Career Inquiries",
                value="careers@lunaxcode.com",
                icon="Mail",
                isPrimary=False,
                displayOrder=10,
                isActive=True
            )
        ]
        
        # Use the base service for contact info
        service = BaseService(
            db=self.db,
            table_name="contact_info",
            model_class=ContactInfo,
            create_model_class=ContactInfoCreate,
            update_model_class=ContactInfoUpdate
        )
        for contact in contacts:
            try:
                await service.create(contact)
                print(f"  ✅ Created: {contact.label}")
            except Exception as e:
                print(f"  ❌ Failed to create {contact.label}: {e}")
        
        print(f"✅ Seeded {len(contacts)} contact info entries")
    
    async def seed_faqs(self):
        """Seed FAQs data."""
        faqs = [
            FAQCreate(
                question="How long does it take to build a website?",
                answer="The timeline depends on the complexity of your project. A basic landing page takes 2-3 days, while complex web applications can take 2-4 weeks. We'll provide a detailed timeline during our initial consultation.",
                category=FAQCategory.GENERAL,
                displayOrder=1,
                isActive=True
            ),
            FAQCreate(
                question="What's included in the pricing?",
                answer="All our packages include custom design, mobile responsiveness, basic SEO optimization, and deployment. Additional features like advanced integrations, e-commerce functionality, or custom animations may have additional costs.",
                category=FAQCategory.PRICING,
                displayOrder=2,
                isActive=True
            ),
            FAQCreate(
                question="Do you provide ongoing maintenance?",
                answer="Yes! We offer monthly maintenance packages that include updates, security monitoring, backups, and technical support. You can also request one-time updates as needed.",
                category=FAQCategory.GENERAL,
                displayOrder=3,
                isActive=True
            ),
            FAQCreate(
                question="Can you work with my existing hosting provider?",
                answer="Absolutely! We can deploy your website to any hosting provider you prefer. We can also recommend reliable hosting solutions if you don't have one yet.",
                category=FAQCategory.TECHNICAL,
                displayOrder=4,
                isActive=True
            ),
            FAQCreate(
                question="What's your development process like?",
                answer="We follow a structured 7-step process: Discovery & Planning, Design & Prototyping, Development, Testing, Deployment, Training, and Ongoing Support. You'll be involved throughout the entire process.",
                category=FAQCategory.PROCESS,
                displayOrder=5,
                isActive=True
            ),
            FAQCreate(
                question="Do you offer refunds?",
                answer="We offer a satisfaction guarantee. If you're not happy with the initial design concepts, we'll refund your deposit. Once development begins and milestones are approved, refunds are subject to work completed.",
                category=FAQCategory.PRICING,
                displayOrder=6,
                isActive=True
            ),
            FAQCreate(
                question="Can I update my website content myself?",
                answer="Yes! We build user-friendly admin panels that allow you to easily update content, images, and basic settings. We also provide training and documentation to help you manage your site.",
                category=FAQCategory.TECHNICAL,
                displayOrder=7,
                isActive=True
            ),
            FAQCreate(
                question="Do you build mobile apps?",
                answer="Yes, we develop cross-platform mobile applications for both iOS and Android using modern frameworks like React Native. These apps work seamlessly across all devices.",
                category=FAQCategory.GENERAL,
                displayOrder=8,
                isActive=True
            ),
            FAQCreate(
                question="What payment methods do you accept?",
                answer="We accept bank transfers, PayPal, and major credit cards. Payment is typically split into milestones: 50% upfront, 30% at midpoint, and 20% upon completion.",
                category=FAQCategory.PRICING,
                displayOrder=9,
                isActive=True
            ),
            FAQCreate(
                question="How do you ensure my website is secure?",
                answer="We implement industry-standard security practices including SSL certificates, secure coding practices, regular updates, and security monitoring. For web applications, we also include user authentication and data encryption.",
                category=FAQCategory.TECHNICAL,
                displayOrder=10,
                isActive=True
            )
        ]
        
        # Use the base service for FAQs
        service = BaseService(
            db=self.db,
            table_name="faqs",
            model_class=FAQ,
            create_model_class=FAQCreate,
            update_model_class=FAQUpdate
        )
        for faq in faqs:
            try:
                await service.create(faq)
                print(f"  ✅ Created: {faq.question[:50]}...")
            except Exception as e:
                print(f"  ❌ Failed to create FAQ: {e}")
        
        print(f"✅ Seeded {len(faqs)} FAQs")
    
    async def seed_site_settings(self):
        """Seed site settings data."""
        settings = [
            SiteSettingCreate(
                key="site_name",
                value="Lunaxcode",
                type=SettingType.TEXT,
                description="Website name displayed in header and title",
                isPublic=True
            ),
            SiteSettingCreate(
                key="site_tagline",
                value="Professional Web & Mobile Development",
                type=SettingType.TEXT,
                description="Site tagline or subtitle",
                isPublic=True
            ),
            SiteSettingCreate(
                key="contact_email",
                value="hello@lunaxcode.com",
                type=SettingType.TEXT,
                description="Primary contact email address",
                isPublic=True
            ),
            SiteSettingCreate(
                key="contact_phone",
                value="+63 917 123 4567",
                type=SettingType.TEXT,
                description="Primary contact phone number",
                isPublic=True
            ),
            SiteSettingCreate(
                key="business_hours",
                value="Monday - Friday: 9:00 AM - 6:00 PM PST",
                type=SettingType.TEXT,
                description="Business operating hours",
                isPublic=True
            ),
            SiteSettingCreate(
                key="max_projects_per_month",
                value="5",
                type=SettingType.NUMBER,
                description="Maximum number of projects taken per month",
                isPublic=False
            ),
            SiteSettingCreate(
                key="featured_testimonials_count",
                value="3",
                type=SettingType.NUMBER,
                description="Number of testimonials to display on homepage",
                isPublic=False
            ),
            SiteSettingCreate(
                key="maintenance_mode",
                value="false",
                type=SettingType.BOOLEAN,
                description="Enable maintenance mode for website",
                isPublic=False
            ),
            SiteSettingCreate(
                key="google_analytics_id",
                value="GA-XXXXXXXXX",
                type=SettingType.TEXT,
                description="Google Analytics tracking ID",
                isPublic=False
            ),
            SiteSettingCreate(
                key="social_links",
                value='{"facebook": "https://facebook.com/lunaxcode", "instagram": "https://instagram.com/lunaxcode", "linkedin": "https://linkedin.com/company/lunaxcode"}',
                type=SettingType.JSON,
                description="Social media links configuration",
                isPublic=True
            )
        ]
        
        # Use the base service for site settings
        service = BaseService(
            db=self.db,
            table_name="site_settings",
            model_class=SiteSetting,
            create_model_class=SiteSettingCreate,
            update_model_class=SiteSettingUpdate
        )
        for setting in settings:
            try:
                await service.create(setting)
                print(f"  ✅ Created: {setting.key}")
            except Exception as e:
                print(f"  ❌ Failed to create {setting.key}: {e}")
        
        print(f"✅ Seeded {len(settings)} site settings")
    
    async def seed_addon_services(self):
        """Seed addon services data."""
        services = [
            AddonServiceCreate(
                serviceId="seo_optimization",
                name="SEO Optimization",
                price="₱5,999",
                description="Advanced SEO optimization including keyword research, meta tags, and search engine submissions",
                unit=ServiceUnit.ONE_TIME,
                category=ServiceCategory.SEO,
                icon="Search",
                popular=True,
                displayOrder=1,
                isActive=True
            ),
            AddonServiceCreate(
                serviceId="logo_design",
                name="Custom Logo Design",
                price="₱3,999",
                description="Professional logo design with multiple concepts and unlimited revisions",
                unit=ServiceUnit.ONE_TIME,
                category=ServiceCategory.GENERAL,
                icon="Palette",
                popular=False,
                displayOrder=2,
                isActive=True
            ),
            AddonServiceCreate(
                serviceId="content_writing",
                name="Content Writing",
                price="₱999",
                description="Professional copywriting for web pages, blogs, and marketing materials",
                unit=ServiceUnit.PER_PAGE,
                category=ServiceCategory.GENERAL,
                icon="PenTool",
                popular=False,
                displayOrder=3,
                isActive=True
            ),
            AddonServiceCreate(
                serviceId="ssl_certificate",
                name="SSL Certificate Setup",
                price="₱1,499",
                description="Professional SSL certificate installation for secure HTTPS connection",
                unit=ServiceUnit.ONE_TIME,
                category=ServiceCategory.GENERAL,
                icon="Shield",
                popular=True,
                displayOrder=4,
                isActive=True
            ),
            AddonServiceCreate(
                serviceId="email_setup",
                name="Professional Email Setup",
                price="₱2,499",
                description="Custom email accounts with your domain name and email client configuration",
                unit=ServiceUnit.ONE_TIME,
                category=ServiceCategory.GENERAL,
                icon="Mail",
                popular=True,
                displayOrder=5,
                isActive=True
            ),
            AddonServiceCreate(
                serviceId="analytics_setup",
                name="Analytics & Tracking Setup",
                price="₱1,999",
                description="Google Analytics, Facebook Pixel, and other tracking tools configuration",
                unit=ServiceUnit.ONE_TIME,
                category=ServiceCategory.SEO,
                icon="BarChart3",
                popular=False,
                displayOrder=6,
                isActive=True
            ),
            AddonServiceCreate(
                serviceId="backup_service",
                name="Automated Backup Service",
                price="₱499",
                description="Daily automated backups with cloud storage and easy restore options",
                unit=ServiceUnit.PER_MONTH,
                category=ServiceCategory.MAINTENANCE,
                icon="HardDrive",
                popular=False,
                displayOrder=7,
                isActive=True
            ),
            AddonServiceCreate(
                serviceId="api_integration",
                name="Third-party API Integration",
                price="₱4,999",
                description="Integration with payment gateways, CRM systems, or other third-party services",
                unit=ServiceUnit.ONE_TIME,
                category=ServiceCategory.INTEGRATION,
                icon="Puzzle",
                popular=True,
                displayOrder=8,
                isActive=True
            ),
            AddonServiceCreate(
                serviceId="performance_optimization",
                name="Performance Optimization",
                price="₱3,499",
                description="Website speed optimization, image compression, and caching setup",
                unit=ServiceUnit.ONE_TIME,
                category=ServiceCategory.MAINTENANCE,
                icon="Zap",
                popular=False,
                displayOrder=9,
                isActive=True
            ),
            AddonServiceCreate(
                serviceId="training_session",
                name="One-on-One Training Session",
                price="₱1,999",
                description="Personal training session to learn how to manage and update your website",
                unit=ServiceUnit.ONE_TIME,
                category=ServiceCategory.GENERAL,
                icon="GraduationCap",
                popular=False,
                displayOrder=10,
                isActive=True
            )
        ]
        
        # Use the base service for addon services
        base_service = BaseService(
            db=self.db,
            table_name="addon_services",
            model_class=AddonService,
            create_model_class=AddonServiceCreate,
            update_model_class=AddonServiceUpdate
        )
        for service in services:
            try:
                await base_service.create(service)
                print(f"  ✅ Created: {service.name}")
            except Exception as e:
                print(f"  ❌ Failed to create {service.name}: {e}")
        
        print(f"✅ Seeded {len(services)} addon services")
    
    async def run_seed(self):
        """Run the complete seeding process."""
        print("🌱 Starting database seeding process...")
        
        try:
            await self.connect()
            
            # Clear existing data
            print("\n🧹 Clearing existing data...")
            await self.clear_all_tables()
            
            # Seed all tables
            print("\n📝 Seeding new data...")
            await self.seed_pricing_plans()
            await self.seed_features()
            await self.seed_process_steps()
            await self.seed_hero_sections()
            await self.seed_testimonials()
            await self.seed_contact_info()
            await self.seed_faqs()
            await self.seed_site_settings()
            await self.seed_addon_services()
            
            print("\n🎉 Database seeding completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Error during seeding: {e}")
            raise
        finally:
            if self.db and hasattr(self.db, 'close'):
                await self.db.close()
                print("🔌 Database connection closed")


async def main():
    """Main function to run the seed script."""
    seeder = SeedData()
    await seeder.run_seed()


if __name__ == "__main__":
    asyncio.run(main())
