import os
import tempfile
import sys
from dotenv import load_dotenv

# Load environment variables from .env file if it exists (only in development)
if not os.environ.get('RENDER'):
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

    # Remove quotes if present in BASE_URL
    if BASE_URL and BASE_URL.startswith("'") and BASE_URL.endswith("'"):
        BASE_URL = BASE_URL[1:-1]

    # Ensure BASE_URL doesn't have a trailing slash
    if BASE_URL and BASE_URL.endswith('/'):
        BASE_URL = BASE_URL[:-1]

    # Detect environment - Render sets this environment variable
    RENDER = os.environ.get('RENDER', 'false').lower() == 'true'

    # Set upload folder based on environment
    if RENDER:
        # On Render, use a subdirectory in the temp directory
        UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), 'pdf_quiz_uploads')
        print(f"Running on Render. Upload folder: {UPLOAD_FOLDER}", file=sys.stderr)
    else:
        # In development, use a local directory
        UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app/static/uploads')
        print(f"Running locally. Upload folder: {UPLOAD_FOLDER}", file=sys.stderr)
