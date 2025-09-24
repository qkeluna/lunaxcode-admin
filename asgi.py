"""
ASGI config for production deployment.
This file is used by ASGI-compatible web servers to serve the project.
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path to ensure imports work
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

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
