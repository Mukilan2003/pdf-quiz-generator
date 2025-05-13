import os
import json
import requests
import secrets
import hashlib
from flask import current_app, url_for, session

class FirebaseIntegration:
    """Class for Firebase integration."""

    def __init__(self):
        """Initialize Firebase configuration."""
        self.api_key = os.environ.get('FIREBASE_API_KEY')
        if not self.api_key and 'FIREBASE_API_KEY' in current_app.config:
            self.api_key = current_app.config['FIREBASE_API_KEY']

        # Remove quotes if present
        if self.api_key and self.api_key.startswith("'") and self.api_key.endswith("'"):
            self.api_key = self.api_key[1:-1]

        self.auth_domain = os.environ.get('FIREBASE_AUTH_DOMAIN')
        if not self.auth_domain and 'FIREBASE_AUTH_DOMAIN' in current_app.config:
            self.auth_domain = current_app.config['FIREBASE_AUTH_DOMAIN']
        if self.auth_domain and self.auth_domain.startswith("'") and self.auth_domain.endswith("'"):
            self.auth_domain = self.auth_domain[1:-1]

        self.project_id = os.environ.get('FIREBASE_PROJECT_ID')
        if not self.project_id and 'FIREBASE_PROJECT_ID' in current_app.config:
            self.project_id = current_app.config['FIREBASE_PROJECT_ID']
        if self.project_id and self.project_id.startswith("'") and self.project_id.endswith("'"):
            self.project_id = self.project_id[1:-1]

        self.storage_bucket = os.environ.get('FIREBASE_STORAGE_BUCKET')
        if not self.storage_bucket and 'FIREBASE_STORAGE_BUCKET' in current_app.config:
            self.storage_bucket = current_app.config['FIREBASE_STORAGE_BUCKET']
        if self.storage_bucket and self.storage_bucket.startswith("'") and self.storage_bucket.endswith("'"):
            self.storage_bucket = self.storage_bucket[1:-1]

        # Google OAuth configuration
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

    def sign_in_with_email_password(self, email, password):
        """Sign in with email and password."""
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.api_key}"
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        response = requests.post(url, json=payload)
        return response.json()

    def sign_up_with_email_password(self, email, password):
        """Sign up with email and password."""
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.api_key}"
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        response = requests.post(url, json=payload)
        return response.json()

    def upload_file_to_storage(self, file_path, destination_path, id_token):
        """Upload a file to Firebase Storage."""
        # This is a simplified implementation
        # In a real application, you would use the Firebase Admin SDK
        # or the Firebase Storage REST API
        try:
            url = f"https://firebasestorage.googleapis.com/v0/b/{self.storage_bucket}/o?name={destination_path}"
            headers = {
                "Authorization": f"Bearer {id_token}",
                "Content-Type": "application/octet-stream"
            }
            with open(file_path, 'rb') as file:
                response = requests.post(url, headers=headers, data=file)
            return response.json()
        except Exception as e:
            print(f"Error uploading file to Firebase Storage: {e}")
            return {"error": str(e)}

    def save_quiz_results(self, user_id, quiz_data, id_token):
        """Save quiz results to Firebase Firestore."""
        # This is a simplified implementation
        # In a real application, you would use the Firebase Admin SDK
        # or the Firestore REST API
        try:
            url = f"https://firestore.googleapis.com/v1/projects/{self.project_id}/databases/(default)/documents/quiz_results/{user_id}"
            headers = {
                "Authorization": f"Bearer {id_token}",
                "Content-Type": "application/json"
            }
            payload = {
                "fields": {
                    "timestamp": {"timestampValue": {"now": True}},
                    "quiz_data": {"mapValue": {"fields": self._convert_to_firestore_format(quiz_data)}}
                }
            }
            response = requests.post(url, headers=headers, json=payload)
            return response.json()
        except Exception as e:
            print(f"Error saving quiz results to Firestore: {e}")
            return {"error": str(e)}

    def get_google_auth_url(self, redirect_uri):
        """Get the Google OAuth URL for sign-in."""
        if not self.google_client_id:
            raise ValueError("Google Client ID is not configured. Please set GOOGLE_CLIENT_ID in your environment variables.")

        # Use the proper OAuth 2.0 client ID instead of Firebase API key
        return (
            f"https://accounts.google.com/o/oauth2/auth"
            f"?client_id={self.google_client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&response_type=id_token token"
            f"&scope=email profile openid"
            f"&prompt=select_account"
            f"&include_granted_scopes=true"
            f"&state={self._generate_state_token()}"
        )

    def verify_google_token(self, id_token):
        """Verify the Google ID token."""
        try:
            # First, verify with Google's tokeninfo endpoint
            google_verify_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
            google_response = requests.get(google_verify_url)
            google_data = google_response.json()

            # Check if the token is valid and issued for our client
            if google_response.status_code != 200:
                return {"error": {"message": f"Invalid token: {google_data.get('error_description', 'Unknown error')}"}}

            if google_data.get('aud') != self.google_client_id:
                return {"error": {"message": "Token was not issued for this application"}}

            # Now sign in with Firebase using the verified token
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp?key={self.api_key}"
            payload = {
                "postBody": f"id_token={id_token}&providerId=google.com",
                "requestUri": current_app.config.get('BASE_URL', 'http://localhost:5000'),
                "returnIdpCredential": True,
                "returnSecureToken": True
            }
            response = requests.post(url, json=payload)
            firebase_data = response.json()

            # If Firebase authentication fails, still use Google data
            if 'error' in firebase_data:
                # Create a user-like response from Google data
                return {
                    "localId": google_data.get('sub'),
                    "email": google_data.get('email'),
                    "displayName": google_data.get('name'),
                    "photoUrl": google_data.get('picture'),
                    "idToken": id_token,
                    # No refresh token in this case
                }

            return firebase_data

        except Exception as e:
            print(f"Error verifying Google token: {e}")
            return {"error": {"message": f"Token verification failed: {str(e)}"}}

    def get_user_profile(self, id_token):
        """Get user profile information."""
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={self.api_key}"
        payload = {
            "idToken": id_token
        }
        response = requests.post(url, json=payload)
        return response.json()

    def store_user_session(self, user_data):
        """Store user data in session."""
        session['user'] = {
            'uid': user_data.get('localId'),
            'email': user_data.get('email'),
            'display_name': user_data.get('displayName'),
            'photo_url': user_data.get('photoUrl'),
            'id_token': user_data.get('idToken'),
            'refresh_token': user_data.get('refreshToken')
        }
        return session['user']

    def refresh_token(self, refresh_token):
        """Refresh the ID token."""
        url = f"https://securetoken.googleapis.com/v1/token?key={self.api_key}"
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        response = requests.post(url, json=payload)
        return response.json()

    def _generate_state_token(self):
        """Generate a secure state token for OAuth."""
        # Generate a random token
        token = secrets.token_hex(16)
        # Store in session for verification when the callback is received
        session['oauth_state'] = token
        return token

    def _convert_to_firestore_format(self, data):
        """Convert Python data types to Firestore format."""
        # This is a simplified implementation
        # In a real application, you would need a more comprehensive conversion
        if isinstance(data, dict):
            return {k: self._convert_to_firestore_format(v) for k, v in data.items()}
        elif isinstance(data, list):
            return {"arrayValue": {"values": [self._convert_to_firestore_format(item) for item in data]}}
        elif isinstance(data, str):
            return {"stringValue": data}
        elif isinstance(data, int):
            return {"integerValue": str(data)}
        elif isinstance(data, float):
            return {"doubleValue": data}
        elif isinstance(data, bool):
            return {"booleanValue": data}
        elif data is None:
            return {"nullValue": None}
        else:
            return {"stringValue": str(data)}
