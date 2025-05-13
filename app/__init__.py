from flask import Flask
from flask_session import Session
from config import Config
import os
import tempfile
import logging
import sys

def create_app(config_class=Config):
    """Create and configure the Flask application."""
    # Configure logging first
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

    # Create Flask app
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Log app creation
    app.logger.info("Creating Flask application...")

    # Create upload directory immediately (without using current_app)
    try:
        upload_folder = app.config.get('UPLOAD_FOLDER')
        if upload_folder:
            os.makedirs(upload_folder, exist_ok=True)
            app.logger.info(f"Created upload directory: {upload_folder}")
    except Exception as e:
        app.logger.warning(f"Could not create upload directory: {e}")

    # Use filesystem for session storage to handle large session data
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = tempfile.gettempdir()
    app.config['SESSION_PERMANENT'] = False

    # Initialize Flask-Session
    Session(app)

    # Register blueprints
    with app.app_context():
        app.logger.info("Registering blueprints...")
        from app.routes import main
        from app.auth import auth

        app.register_blueprint(main)
        app.register_blueprint(auth, url_prefix='/auth')

    # Log that app creation is complete
    app.logger.info("Application created successfully")

    return app
