"""
Vercel-compatible entry point for FastAPI application.
Minimal version to avoid import issues.
"""

# Create a minimal FastAPI app directly to avoid import issues
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time

# Create minimal app
app = FastAPI(
    title="Lunaxcode CMS Admin API",
    description="Content Management System API for Lunaxcode",
    version="1.0.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basic endpoints
@app.get("/")
async def root():
    return {
        "message": "Lunaxcode CMS Admin API",
        "status": "running",
        "platform": "vercel",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "platform": "vercel"
    }

# API endpoints with static data
@app.get("/api/v1/pricing-plans/")
async def get_pricing_plans():
    return {
        "items": [
            {
                "planId": "landing_basic",
                "name": "Landing Page Basic", 
                "price": "₱9,999",
                "period": "one-time",
                "description": "Perfect for small businesses needing a professional online presence",
                "features": [
                    "Custom design",
                    "Mobile responsive", 
                    "Contact form",
                    "SEO optimized",
                    "48-hour delivery"
                ],
                "buttonText": "Get Started",
                "buttonVariant": "outline",
                "popular": False,
                "timeline": "48 hours",
                "displayOrder": 1,
                "category": "web",
                "isActive": True
            },
            {
                "planId": "landing_premium",
                "name": "Landing Page Premium",
                "price": "₱19,999",
                "period": "one-time",
                "description": "Advanced landing page with interactive elements",
                "features": [
                    "Everything in Basic",
                    "Advanced animations",
                    "Interactive elements",
                    "A/B testing setup"
                ],
                "buttonText": "Choose Premium",
                "buttonVariant": "default",
                "popular": True,
                "timeline": "72 hours",
                "displayOrder": 2,
                "category": "web",
                "isActive": True
            }
        ],
        "total": 2,
        "page": 1,
        "size": 20
    }

@app.get("/api/v1/features/")
async def get_features():
    return {
        "items": [
            {
                "title": "Lightning Fast Development",
                "description": "Get your project up and running in record time with our streamlined development process.",
                "icon": "Zap",
                "color": "from-yellow-400 to-orange-500",
                "displayOrder": 1,
                "isActive": True
            },
            {
                "title": "Mobile-First Design",
                "description": "Every project is built with mobile users in mind, ensuring perfect functionality across all devices.",
                "icon": "Smartphone",
                "color": "from-blue-400 to-purple-500",
                "displayOrder": 2,
                "isActive": True
            }
        ],
        "total": 2,
        "page": 1,
        "size": 20
    }

@app.get("/api/v1/testimonials/")
async def get_testimonials():
    return {
        "items": [
            {
                "clientName": "Maria Santos",
                "clientCompany": "Santos Bakery",
                "clientRole": "Owner", 
                "testimonial": "The landing page they created for our bakery increased our online orders by 200%. Highly recommend!",
                "rating": 5,
                "avatar": "https://images.unsplash.com/photo-1494790108755-2616b612b789?w=150",
                "projectType": "landing_page",
                "displayOrder": 1,
                "isActive": True
            }
        ],
        "total": 1,
        "page": 1,
        "size": 20
    }

@app.get("/api/v1/contact-info/")
async def get_contact_info():
    return {
        "items": [
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
                "displayOrder": 2,
                "isActive": True
            }
        ],
        "total": 2,
        "page": 1,
        "size": 20
    }

@app.get("/api/v1/faqs/")
async def get_faqs():
    return {
        "items": [
            {
                "question": "How long does it take to build a website?",
                "answer": "The timeline depends on the complexity of your project. A basic landing page takes 2-3 days, while complex web applications can take 2-4 weeks.",
                "category": "general",
                "displayOrder": 1,
                "isActive": True
            },
            {
                "question": "What's included in the pricing?",
                "answer": "All our packages include custom design, mobile responsiveness, basic SEO optimization, and deployment.",
                "category": "pricing",
                "displayOrder": 2,
                "isActive": True
            }
        ],
        "total": 2,
        "page": 1,
        "size": 20
    }

# Export for Vercel
handler = app
