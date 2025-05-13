"""
Special entry point for Render deployment that avoids application context issues.
This file is designed to be used with Gunicorn on Render.
"""
import os
import sys
import logging

# Configure logging before anything else
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Set environment variable to indicate we're running on Render
os.environ['RENDER'] = 'true'

logger.info("Starting application with render_app.py entry point")

# Import the Flask app factory function
from app import create_app

# Create the Flask application instance
app = create_app()

# This ensures the application context is properly set up
# when running with Gunicorn
application = app  # For WSGI compatibility

# Log that the application has been created
logger.info("Application instance created successfully")

# No if __name__ == '__main__' block to avoid any potential issues
