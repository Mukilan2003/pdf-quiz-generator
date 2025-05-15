import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Set environment variable to indicate we're running on Vercel
os.environ['VERCEL'] = 'true'

logger.info("Starting application with wsgi.py entry point")

# Import the Flask app factory function
from app import create_app

# Create the Flask application instance
app = create_app()

# This ensures the application context is properly set up
application = app  # For WSGI compatibility

# Log that the application has been created
logger.info("Application instance created successfully")

if __name__ == '__main__':
    app.run(debug=True)
