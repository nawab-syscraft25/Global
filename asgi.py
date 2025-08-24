"""
ASGI config for Global Pooja application.

This module contains the ASGI application used by ASGI-compatible web servers
to serve the project in production.

ASGI is the preferred way to deploy FastAPI applications.
"""

import os
import sys
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Set environment variables if needed
os.environ.setdefault('PYTHONPATH', str(project_dir))

# Import the FastAPI application
from app.main import app

# ASGI application
application = app

if __name__ == "__main__":
    # For development/testing
    import uvicorn
    uvicorn.run(
        "asgi:application",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )
