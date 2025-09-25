"""
FastAPI application for Lunaxcode CMS Admin Backend.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time
import logging
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.exceptions import (
    CustomHTTPException,
    custom_http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from app.core.logging import setup_logging
from app.api import api_router
from app.core.cache import redis_client, init_cache
from app.database.postgres import init_database, close_database, db_manager

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("🚀 Starting Lunaxcode CMS Admin API...")
    
    # Startup
    try:
        # Initialize database
        await init_database()
        logger.info("✅ PostgreSQL database initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
    
    try:
        # Initialize cache
        await init_cache()
        logger.info("✅ Cache system initialized")
    except Exception as e:
        logger.warning(f"⚠️  Cache initialization failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Lunaxcode CMS Admin API...")
    try:
        await close_database()
        logger.info("✅ PostgreSQL connection closed")
    except Exception as e:
        logger.error(f"❌ Error closing database connection: {e}")
    
    try:
        await redis_client.close()
        logger.info("✅ Redis connection closed")
    except Exception as e:
        logger.error(f"❌ Error closing Redis connection: {e}")


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="CMS Admin API for Lunaxcode.com - Manage content, pricing, and site settings",
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Exception handlers
app.add_exception_handler(CustomHTTPException, custom_http_exception_handler)
app.add_exception_handler(422, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "message": "Lunaxcode CMS Admin API",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_STR}/docs",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test PostgreSQL connection
        database_status = "connected"
        try:
            await db_manager.health_check()
        except Exception:
            database_status = "disconnected"
        
        # Test Redis connection
        redis_status = "connected"
        try:
            await redis_client.ping()
        except Exception:
            redis_status = "disconnected"
        
        overall_status = "healthy" if database_status == "connected" else "unhealthy"
        
        return {
            "status": overall_status,
            "timestamp": time.time(),
            "services": {
                "database": database_status,
                "redis": redis_status,
                "api": "operational"
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
        )


if __name__ == "__main__":
    import uvicorn
    import os
    
    # Get port from environment variable (for deployment) or default to 8000
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.DEBUG,
        log_level="info"
    )
