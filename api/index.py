"""
Vercel-compatible entry point for FastAPI application.
This file is specifically designed for Vercel serverless deployment.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the FastAPI app
try:
    # Try the full app first
    from app.main import app
    handler = app
    
except ImportError:
    try:
        # Fallback to Vercel-optimized app
        from app.main_vercel import app
        handler = app
        
    except ImportError as e:
        # Final fallback minimal app
        from fastapi import FastAPI
        from fastapi.responses import JSONResponse
        
        app = FastAPI(title="Lunaxcode CMS API - Vercel")
        
        @app.get("/")
        async def root():
            return {"message": "Lunaxcode CMS API is running on Vercel", "status": "ok"}
        
        @app.get("/health")
        async def health():
            return {"status": "healthy", "platform": "vercel"}
        
        handler = app
