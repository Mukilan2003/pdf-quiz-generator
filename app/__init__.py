from flask import Flask, current_app
from flask_session import Session
from config import Config
import os
import tempfile

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

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

    # Setup function to create upload directory
    def setup_upload_directory():
        """Ensure upload directory exists."""
        try:
            os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
        except Exception as e:
            app.logger.warning(f"Could not create upload directory: {e}")

    # Register setup function to run before first request
    app.before_request_funcs.setdefault(None, []).append(lambda: setup_upload_directory())

    return app
