import os
import tempfile
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Config:
    # Basic configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size

    # API keys
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

    # Google OAuth configuration
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')

    # Application base URL (for OAuth redirect)
    BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5000')

    # Detect environment
    RENDER = os.environ.get('RENDER', 'false').lower() == 'true'

    # Set upload folder based on environment
    if RENDER:
        UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), 'uploads')
    else:
        UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app/static/uploads')
