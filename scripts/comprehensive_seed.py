#!/usr/bin/env python3
"""
Working Seed Data Script - Following the FAQ pattern but using correct imports

This script populates all content tables with realistic seed data
using the same pattern as the working seed_faq_data.py
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

# Add the parent directory to the path so we can import app modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import using your actual project structure
from app.database.xata import get_database
from app.services.base import BaseService
from app.services.pricing_plans import PricingPlansService
from app.models.content import (
    PricingPlanCreate, PricingPlan, PricingPlanUpdate, PlanCategory, ButtonVariant,
    FeatureCreate, Feature, FeatureUpdate,
    TestimonialCreate, Testimonial, TestimonialUpdate, ProjectType,
    ContactInfoCreate, ContactInfo, ContactInfoUpdate, ContactType,
    FAQCreate, FAQ, FAQUpdate, FAQCategory,
)

# Seed data for different tables
PRICING_PLANS_DATA = [
    {
        "planId": "mobile_basic",
        "name": "Mobile App Basic",
        "price": "₱79,999",
        "period": "project-based",
        "description": "Professional mobile app for iOS and Android with essential features",
        "features": [
            "Native iOS & Android apps",
            "User authentication",
            "Push notifications",
            "Basic analytics",
            "App store submission"
        ],
        "buttonText": "Start Mobile Project",
        "buttonVariant": "outline",
        "popular": False,
        "timeline": "3-4 weeks",
        "displayOrder": 4,
        "category": "mobile",
        "isActive": True
    },
    {
        "planId": "ecommerce_starter",
        "name": "E-commerce Starter",
        "price": "₱99,999",
        "period": "project-based", 
        "description": "Complete online store with payment integration and inventory management",
        "features": [
            "Product catalog",
            "Shopping cart",
            "Payment gateway",
            "Order management",
            "Inventory tracking",
            "Customer accounts"
        ],
        "buttonText": "Launch Store",
        "buttonVariant": "default",
        "popular": True,
        "timeline": "2-3 weeks",
        "displayOrder": 5,
        "category": "web",
        "isActive": True
    },
    {
        "planId": "maintenance_monthly",
        "name": "Monthly Maintenance",
        "price": "₱4,999",
        "period": "monthly",
        "description": "Keep your website secure, updated, and running smoothly",
        "features": [
            "Security updates",
            "Content updates",
            "Performance monitoring",
            "Monthly backups",
            "Technical support"
        ],
        "buttonText": "Subscribe",
        "buttonVariant": "outline", 
        "popular": False,
        "timeline": "ongoing",
        "displayOrder": 6,
        "category": "web",
        "isActive": True
    }
]

FEATURES_DATA = [
    {
        "title": "Lightning Fast Development",
        "description": "Get your project up and running in record time with our streamlined development process and proven frameworks.",
        "icon": "Zap",
        "color": "from-yellow-400 to-orange-500",
        "displayOrder": 1,
        "isActive": True
    },
    {
        "title": "Mobile-First Design",
        "description": "Every project is built with mobile users in mind, ensuring perfect functionality across all devices and screen sizes.",
        "icon": "Smartphone", 
        "color": "from-blue-400 to-purple-500",
        "displayOrder": 2,
        "isActive": True
    },
    {
        "title": "SEO Optimized",
        "description": "Built-in SEO best practices to help your website rank higher in search results and attract more organic traffic.",
        "icon": "Search",
        "color": "from-green-400 to-blue-500", 
        "displayOrder": 3,
        "isActive": True
    }
]

TESTIMONIALS_DATA = [
    {
        "clientName": "Maria Santos",
        "clientCompany": "Santos Bakery",
        "clientRole": "Owner",
        "testimonial": "The landing page they created for our bakery increased our online orders by 200%. The design is beautiful and works perfectly on mobile. Highly recommend!",
        "rating": 5,
        "avatar": "https://images.unsplash.com/photo-1494790108755-2616b612b789?w=150",
        "projectType": "landing_page",
        "displayOrder": 1,
        "isActive": True
    },
    {
        "clientName": "Carlos Rodriguez", 
        "clientCompany": "TechStart Solutions",
        "clientRole": "CEO",
        "testimonial": "Our web application was delivered on time and exceeded expectations. The team's attention to detail and communication throughout the project was exceptional.",
        "rating": 5,
        "avatar": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150",
        "projectType": "web_app",
        "displayOrder": 2,
        "isActive": True
    }
]

CONTACT_INFO_DATA = [
    {
        "type": "email",
        "label": "Business Email",
        "value": "hello@lunaxcode.com",
        "icon": "Mail",
        "isPrimary": True,
        "displayOrder": 1,
        "isActive": True
    },
    {
        "type": "phone",
        "label": "Primary Phone",
        "value": "+63 917 123 4567", 
        "icon": "Phone",
        "isPrimary": True,
        "displayOrder": 3,
        "isActive": True
    }
]

FAQS_DATA = [
    {
        "question": "How long does it take to build a website?",
        "answer": "The timeline depends on the complexity of your project. A basic landing page takes 2-3 days, while complex web applications can take 2-4 weeks. We'll provide a detailed timeline during our initial consultation.",
        "category": "general",
        "displayOrder": 1,
        "isActive": True
    },
    {
        "question": "What's included in the pricing?",
        "answer": "All our packages include custom design, mobile responsiveness, basic SEO optimization, and deployment. Additional features like advanced integrations, e-commerce functionality, or custom animations may have additional costs.",
        "category": "pricing", 
        "displayOrder": 2,
        "isActive": True
    },
    {
        "question": "Do you provide ongoing maintenance?",
        "answer": "Yes! We offer monthly maintenance packages that include updates, security monitoring, backups, and technical support. You can also request one-time updates as needed.",
        "category": "general",
        "displayOrder": 3,
        "isActive": True
    }
]


async def seed_pricing_plans():
    """Seed pricing plans using the same pattern as FAQ seeder"""
    print("🌱 Starting Pricing Plans Data Seeding Process")
    print(f"📊 Preparing to seed {len(PRICING_PLANS_DATA)} Pricing Plan records")
    
    try:
        # Get database and create service 
        db = await get_database()
        await db.connect()
        
        service = BaseService(
            db=db,
            table_name="pricing_plans",
            model_class=PricingPlan,
            create_model_class=PricingPlanCreate,
            update_model_class=PricingPlanUpdate
        )
        
        # Track seeding statistics
        created_count = 0
        error_count = 0
        
        print("\n🚀 Creating Pricing Plan records...")
        
        for i, plan_data in enumerate(PRICING_PLANS_DATA, 1):
            try:
                # Create Pricing Plan record
                plan_create = PricingPlanCreate(**plan_data)
                result = await service.create(plan_create)
                
                created_count += 1
                print(f"✅ [{i:2d}/{len(PRICING_PLANS_DATA)}] Created Plan: {result.name}...")
                
                # Add small delay to avoid overwhelming the database
                await asyncio.sleep(0.1)
                
            except Exception as e:
                error_count += 1
                print(f"❌ [{i:2d}/{len(PRICING_PLANS_DATA)}] Failed to create Plan: {plan_data['name']}...")
                print(f"   Error: {str(e)}")
                continue
        
        print(f"\n📈 Pricing Plans Seeding Summary:")
        print(f"   ✅ Successfully created: {created_count} Plans")
        print(f"   ❌ Errors encountered: {error_count} Plans")
        print(f"   📊 Success rate: {(created_count / len(PRICING_PLANS_DATA)) * 100:.1f}%")
        
        return created_count > 0
        
    except Exception as e:
        print(f"\n💥 Critical error during pricing plans seeding: {str(e)}")
        return False


async def seed_features():
    """Seed features using the same pattern as FAQ seeder"""
    print("🌱 Starting Features Data Seeding Process")
    print(f"📊 Preparing to seed {len(FEATURES_DATA)} Feature records")
    
    try:
        # Get database and create service 
        db = await get_database()
        await db.connect()
        
        service = BaseService(
            db=db,
            table_name="features",
            model_class=Feature,
            create_model_class=FeatureCreate,
            update_model_class=FeatureUpdate
        )
        
        # Track seeding statistics
        created_count = 0
        error_count = 0
        
        print("\n🚀 Creating Feature records...")
        
        for i, feature_data in enumerate(FEATURES_DATA, 1):
            try:
                # Create Feature record
                feature_create = FeatureCreate(**feature_data)
                result = await service.create(feature_create)
                
                created_count += 1
                print(f"✅ [{i:2d}/{len(FEATURES_DATA)}] Created Feature: {result.title[:50]}...")
                
                # Add small delay to avoid overwhelming the database
                await asyncio.sleep(0.1)
                
            except Exception as e:
                error_count += 1
                print(f"❌ [{i:2d}/{len(FEATURES_DATA)}] Failed to create Feature: {feature_data['title'][:50]}...")
                print(f"   Error: {str(e)}")
                continue
        
        print(f"\n📈 Features Seeding Summary:")
        print(f"   ✅ Successfully created: {created_count} Features")
        print(f"   ❌ Errors encountered: {error_count} Features")
        print(f"   📊 Success rate: {(created_count / len(FEATURES_DATA)) * 100:.1f}%")
        
        return created_count > 0
        
    except Exception as e:
        print(f"\n💥 Critical error during features seeding: {str(e)}")
        return False


async def seed_testimonials():
    """Seed testimonials using the same pattern as FAQ seeder"""
    print("\n🌱 Starting Testimonials Data Seeding Process")
    print(f"📊 Preparing to seed {len(TESTIMONIALS_DATA)} Testimonial records")
    
    try:
        # Get database and create service
        db = await get_database()
        
        service = BaseService(
            db=db,
            table_name="testimonials",
            model_class=Testimonial,
            create_model_class=TestimonialCreate,
            update_model_class=TestimonialUpdate
        )
        
        # Track seeding statistics
        created_count = 0
        error_count = 0
        
        print("\n🚀 Creating Testimonial records...")
        
        for i, testimonial_data in enumerate(TESTIMONIALS_DATA, 1):
            try:
                # Create Testimonial record
                testimonial_create = TestimonialCreate(**testimonial_data)
                result = await service.create(testimonial_create)
                
                created_count += 1
                print(f"✅ [{i:2d}/{len(TESTIMONIALS_DATA)}] Created Testimonial: {result.clientName}...")
                
                # Add small delay to avoid overwhelming the database
                await asyncio.sleep(0.1)
                
            except Exception as e:
                error_count += 1
                print(f"❌ [{i:2d}/{len(TESTIMONIALS_DATA)}] Failed to create Testimonial: {testimonial_data['clientName']}...")
                print(f"   Error: {str(e)}")
                continue
        
        print(f"\n📈 Testimonials Seeding Summary:")
        print(f"   ✅ Successfully created: {created_count} Testimonials")
        print(f"   ❌ Errors encountered: {error_count} Testimonials")
        print(f"   📊 Success rate: {(created_count / len(TESTIMONIALS_DATA)) * 100:.1f}%")
        
        return created_count > 0
        
    except Exception as e:
        print(f"\n💥 Critical error during testimonials seeding: {str(e)}")
        return False


async def seed_contact_info():
    """Seed contact info using the same pattern as FAQ seeder"""
    print("\n🌱 Starting Contact Info Data Seeding Process")
    print(f"📊 Preparing to seed {len(CONTACT_INFO_DATA)} Contact Info records")
    
    try:
        # Get database and create service
        db = await get_database()
        
        service = BaseService(
            db=db,
            table_name="contact_info",
            model_class=ContactInfo,
            create_model_class=ContactInfoCreate,
            update_model_class=ContactInfoUpdate
        )
        
        # Track seeding statistics
        created_count = 0
        error_count = 0
        
        print("\n🚀 Creating Contact Info records...")
        
        for i, contact_data in enumerate(CONTACT_INFO_DATA, 1):
            try:
                # Create Contact Info record
                contact_create = ContactInfoCreate(**contact_data)
                result = await service.create(contact_create)
                
                created_count += 1
                print(f"✅ [{i:2d}/{len(CONTACT_INFO_DATA)}] Created Contact Info: {result.label}...")
                
                # Add small delay to avoid overwhelming the database
                await asyncio.sleep(0.1)
                
            except Exception as e:
                error_count += 1
                print(f"❌ [{i:2d}/{len(CONTACT_INFO_DATA)}] Failed to create Contact Info: {contact_data['label']}...")
                print(f"   Error: {str(e)}")
                continue
        
        print(f"\n📈 Contact Info Seeding Summary:")
        print(f"   ✅ Successfully created: {created_count} Contact Info")
        print(f"   ❌ Errors encountered: {error_count} Contact Info")
        print(f"   📊 Success rate: {(created_count / len(CONTACT_INFO_DATA)) * 100:.1f}%")
        
        return created_count > 0
        
    except Exception as e:
        print(f"\n💥 Critical error during contact info seeding: {str(e)}")
        return False


async def seed_faqs():
    """Seed FAQs using the same pattern as FAQ seeder"""
    print("\n🌱 Starting FAQs Data Seeding Process")
    print(f"📊 Preparing to seed {len(FAQS_DATA)} FAQ records")
    
    try:
        # Get database and create service
        db = await get_database()
        
        service = BaseService(
            db=db,
            table_name="faqs",
            model_class=FAQ,
            create_model_class=FAQCreate,
            update_model_class=FAQUpdate
        )
        
        # Track seeding statistics
        created_count = 0
        error_count = 0
        
        print("\n🚀 Creating FAQ records...")
        
        for i, faq_data in enumerate(FAQS_DATA, 1):
            try:
                # Create FAQ record
                faq_create = FAQCreate(**faq_data)
                result = await service.create(faq_create)
                
                created_count += 1
                print(f"✅ [{i:2d}/{len(FAQS_DATA)}] Created FAQ: {result.question[:50]}...")
                
                # Add small delay to avoid overwhelming the database
                await asyncio.sleep(0.1)
                
            except Exception as e:
                error_count += 1
                print(f"❌ [{i:2d}/{len(FAQS_DATA)}] Failed to create FAQ: {faq_data['question'][:50]}...")
                print(f"   Error: {str(e)}")
                continue
        
        print(f"\n📈 FAQs Seeding Summary:")
        print(f"   ✅ Successfully created: {created_count} FAQs")
        print(f"   ❌ Errors encountered: {error_count} FAQs")
        print(f"   📊 Success rate: {(created_count / len(FAQS_DATA)) * 100:.1f}%")
        
        return created_count > 0
        
    except Exception as e:
        print(f"\n💥 Critical error during FAQs seeding: {str(e)}")
        return False


async def main():
    """Main function to run the seeding process"""
    print("=" * 60)
    print("🌱 Content Database Seeding Script")
    print("=" * 60)
    
    try:
        success_count = 0
        
        # Seed all content types
        if await seed_pricing_plans():
            success_count += 1
            
        if await seed_features():
            success_count += 1
            
        if await seed_testimonials():
            success_count += 1
            
        if await seed_contact_info():
            success_count += 1
            
        if await seed_faqs():
            success_count += 1
        
        print(f"\n🎉 Seeding completed!")
        print(f"📊 Successfully seeded {success_count}/5 content types")
        
        if success_count > 0:
            print(f"\n🌐 You can now test your API endpoints:")
            print(f"   GET /api/v1/pricing-plans/")
            print(f"   GET /api/v1/features/")
            print(f"   GET /api/v1/testimonials/")
            print(f"   GET /api/v1/contact-info/")
            print(f"   GET /api/v1/faqs/")
            return 0
        else:
            print(f"\n❌ No content was seeded. Please check the errors above.")
            return 1
            
    except KeyboardInterrupt:
        print(f"\n⏹️  Seeding interrupted by user.")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        return 1


if __name__ == "__main__":
    # Run the seeding process
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
