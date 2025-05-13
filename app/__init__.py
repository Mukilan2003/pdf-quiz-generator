from flask import Flask
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

    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register blueprints
    from app.routes import main
    from app.auth import auth

    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')

    return app
