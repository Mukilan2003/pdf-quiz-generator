import os
import json
import requests
import secrets
import hashlib
import urllib.parse
from flask import current_app, url_for, session, redirect

class GoogleAuth:
    """Class for Google OAuth authentication."""

    def __init__(self):
        """Initialize Google OAuth configuration."""
        self.google_client_id = os.environ.get('GOOGLE_CLIENT_ID')
        if not self.google_client_id and 'GOOGLE_CLIENT_ID' in current_app.config:
            self.google_client_id = current_app.config['GOOGLE_CLIENT_ID']
        if self.google_client_id and self.google_client_id.startswith("'") and self.google_client_id.endswith("'"):
            self.google_client_id = self.google_client_id[1:-1]

        self.google_client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
        if not self.google_client_secret and 'GOOGLE_CLIENT_SECRET' in current_app.config:
            self.google_client_secret = current_app.config['GOOGLE_CLIENT_SECRET']
        if self.google_client_secret and self.google_client_secret.startswith("'") and self.google_client_secret.endswith("'"):
            self.google_client_secret = self.google_client_secret[1:-1]

    def get_google_auth_url(self, redirect_uri=None):
        """Get the Google OAuth URL for sign-in."""
        if not self.google_client_id:
            raise ValueError("Google Client ID is not configured. Please set GOOGLE_CLIENT_ID in your environment variables.")

        if not redirect_uri:
            base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
            redirect_uri = f"{base_url}/auth/google-callback"

        # URL encode the redirect URI
        encoded_redirect_uri = urllib.parse.quote(redirect_uri, safe='')

        # Log the redirect URI for debugging
        current_app.logger.info(f"OAuth redirect URI: {redirect_uri}")
        current_app.logger.info(f"Encoded OAuth redirect URI: {encoded_redirect_uri}")

        # Generate state token for CSRF protection
        state = self._generate_state_token()

        return (
            f"https://accounts.google.com/o/oauth2/auth"
            f"?client_id={self.google_client_id}"
            f"&redirect_uri={encoded_redirect_uri}"
            f"&response_type=code"
            f"&scope=email profile openid"
            f"&prompt=select_account"
            f"&include_granted_scopes=true"
            f"&state={state}"
        )

    def exchange_code_for_token(self, code, redirect_uri=None):
        """Exchange authorization code for tokens."""
        if not redirect_uri:
            base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
            redirect_uri = f"{base_url}/auth/google-callback"

        # Log the redirect URI for debugging
        current_app.logger.info(f"Token exchange redirect URI: {redirect_uri}")

        token_url = "https://oauth2.googleapis.com/token"
        payload = {
            "client_id": self.google_client_id,
            "client_secret": self.google_client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri
        }

        # Log the payload for debugging (excluding client secret)
        debug_payload = payload.copy()
        debug_payload["client_secret"] = "REDACTED"
        current_app.logger.info(f"Token exchange payload: {debug_payload}")

        response = requests.post(token_url, data=payload)
        if response.status_code != 200:
            error_data = response.json()
            current_app.logger.error(f"Token exchange error: {error_data}")
            return {"error": error_data}

        return response.json()

    def get_user_info(self, access_token):
        """Get user information using the access token."""
        user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}

        response = requests.get(user_info_url, headers=headers)
        if response.status_code != 200:
            return {"error": response.json()}

        return response.json()

    def store_user_session(self, user_info, tokens=None):
        """Store user data in session."""
        session['user'] = {
            'uid': user_info.get('sub'),
            'email': user_info.get('email'),
            'display_name': user_info.get('name'),
            'photo_url': user_info.get('picture'),
        }

        # Store tokens if provided
        if tokens:
            session['tokens'] = {
                'access_token': tokens.get('access_token'),
                'refresh_token': tokens.get('refresh_token'),
                'id_token': tokens.get('id_token'),
                'expires_in': tokens.get('expires_in')
            }

        return session['user']

    def refresh_token(self, refresh_token):
        """Refresh the access token."""
        token_url = "https://oauth2.googleapis.com/token"
        payload = {
            "client_id": self.google_client_id,
            "client_secret": self.google_client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }

        response = requests.post(token_url, data=payload)
        return response.json()

    def _generate_state_token(self):
        """Generate a secure state token for OAuth."""
        # Generate a random token
        token = secrets.token_hex(16)
        # Store in session for verification when the callback is received
        session['oauth_state'] = token
        return token
