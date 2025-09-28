"""
Vercel-optimized FastAPI application for Lunaxcode CMS Admin Backend.
This version is simplified for serverless deployment.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import logging
import os

# Simplified logging for Vercel
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Lunaxcode CMS Admin API",
    description="Content Management System API for Lunaxcode",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration for Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000", 
        "https://lunaxcode.com",
        "https://*.vercel.app",
        "https://*.leapcell.io",
        "*"  # For development - restrict in production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Basic health endpoints
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

# API endpoints - simplified versions
@app.get("/api/v1/pricing-plans/")
async def get_pricing_plans():
    """Simplified pricing plans endpoint for Vercel"""
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
            }
        ],
        "total": 1,
        "page": 1,
        "size": 20
    }

@app.get("/api/v1/features/")
async def get_features():
    """Simplified features endpoint for Vercel"""
    return {
        "items": [
            {
                "title": "Lightning Fast Development",
                "description": "Get your project up and running in record time with our streamlined development process.",
                "icon": "Zap",
                "color": "from-yellow-400 to-orange-500",
                "displayOrder": 1,
                "isActive": True
            }
        ],
        "total": 1,
        "page": 1,
        "size": 20
    }

@app.get("/api/v1/testimonials/")
async def get_testimonials():
    """Simplified testimonials endpoint for Vercel"""
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
    """Simplified contact info endpoint for Vercel"""
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
            }
        ],
        "total": 1,
        "page": 1,
        "size": 20
    }

@app.get("/api/v1/faqs/")
async def get_faqs():
    """Simplified FAQs endpoint for Vercel"""
    return {
        "items": [
            {
                "question": "How long does it take to build a website?",
                "answer": "The timeline depends on the complexity of your project. A basic landing page takes 2-3 days, while complex web applications can take 2-4 weeks.",
                "category": "general",
                "displayOrder": 1,
                "isActive": True
            }
        ],
        "total": 1,
        "page": 1,
        "size": 20
    }

# Exception handlers
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "message": "Internal server error",
                "code": "INTERNAL_ERROR",
                "status_code": 500
            },
            "path": str(request.url.path),
            "method": request.method
        }
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
