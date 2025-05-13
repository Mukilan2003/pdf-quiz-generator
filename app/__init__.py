from flask import Flask, current_app
from flask_session import Session
from config import Config
import os
import tempfile
import logging

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Configure logging
    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)
    app.logger.info("Starting application...")

    # Use filesystem for session storage to handle large session data
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = tempfile.gettempdir()
    app.config['SESSION_PERMANENT'] = False

    # Initialize Flask-Session
    Session(app)

    # Register blueprints
    from app.routes import main
    from app.auth import auth

    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')

    # Create a function to set up the upload directory
    @app.before_request
    def setup_upload_directory():
        """Ensure upload directory exists before handling requests."""
        try:
            upload_folder = current_app.config.get('UPLOAD_FOLDER')
            if upload_folder:
                os.makedirs(upload_folder, exist_ok=True)
                app.logger.info(f"Created upload directory: {upload_folder}")
        except Exception as e:
            app.logger.warning(f"Could not create upload directory: {e}")

    # Log that app creation is complete
    app.logger.info("Application created successfully")

    return app
