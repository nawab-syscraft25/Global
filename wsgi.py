"""
WSGI config for Global Pooja application.

This module contains the WSGI application used by WSGI-compatible web servers
to serve the project in production.

For more information on this file, see:
https://fastapi.tiangolo.com/deployment/server-workers/
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

# WSGI application
application = app

# For compatibility with some WSGI servers
def wsgi_app(environ, start_response):
    """
    WSGI application callable
    """
    return application(environ, start_response)

if __name__ == "__main__":
    # For development/testing with built-in server
    import uvicorn
    uvicorn.run(
        "wsgi:application",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
