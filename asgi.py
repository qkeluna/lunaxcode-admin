"""
ASGI config for production deployment.
This file is used by ASGI-compatible web servers to serve the project.
"""

from app.main import app

# Export the FastAPI application instance for ASGI servers
application = app

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Get port from environment variable (for deployment) or default to 8000
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
