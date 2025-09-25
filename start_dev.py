#!/usr/bin/env python3
"""
Development server startup script.
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

def main():
    """Start the development server."""
    
    # Check if .env file exists
    env_file = app_dir / ".env"
    if not env_file.exists():
        print("⚠️  Warning: .env file not found!")
        print("Please copy .env.example to .env and configure your settings.")
        print()
        
        # Check for required environment variables
        required_vars = ["DATABASE_URL"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
            print("Please set these in your .env file or environment.")
            return
    
    print("🚀 Starting Lunaxcode CMS Admin API...")
    print("📊 Access API docs at: http://localhost:8000/api/v1/docs")
    print("🔄 Access ReDoc at: http://localhost:8000/api/v1/redoc")
    print()
    
    # Start the server
    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down server...")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
