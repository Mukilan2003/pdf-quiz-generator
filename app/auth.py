from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify, current_app
from app.utils.google_auth import GoogleAuth

auth = Blueprint('auth', __name__)
google_auth = GoogleAuth()

@auth.route('/login')
def login():
    """Render login page."""
    if 'user' in session:
        return redirect(url_for('main.index'))
    return render_template('auth/login.html')

@auth.route('/google-login')
def google_login():
    """Initiate Google OAuth login."""
    try:
        # Log the BASE_URL for debugging
        current_app.logger.info(f"BASE_URL from config: {current_app.config.get('BASE_URL')}")

        auth_url = google_auth.get_google_auth_url()
        current_app.logger.info(f"Generated auth URL: {auth_url}")
        return redirect(auth_url)
    except Exception as e:
        current_app.logger.error(f"Error initiating Google login: {str(e)}", exc_info=True)
        flash(f"Error initiating Google login: {str(e)}")
        return redirect(url_for('main.index'))

@auth.route('/google-callback')
def google_callback():
    """Handle Google OAuth callback."""
    current_app.logger.info("Google callback received")

    try:
        # Get the authorization code from the request
        code = request.args.get('code')
        state = request.args.get('state')
        error = request.args.get('error')

        # Log all request parameters for debugging (excluding the code for security)
        debug_args = request.args.copy()
        if 'code' in debug_args:
            debug_args['code'] = 'REDACTED'
        current_app.logger.info(f"Callback parameters: {debug_args}")

        # Check for error parameter
        if error:
            current_app.logger.error(f"Google returned an error: {error}")
            flash(f"Authentication failed: {error}")
            return redirect(url_for('main.index'))

        # Verify state parameter to prevent CSRF
        stored_state = session.get('oauth_state')
        current_app.logger.info(f"Session contents: {list(session.keys())}")

        if not state:
            current_app.logger.error("No state parameter received")
            flash("Authentication failed: No state parameter received. Please try again.")
            return redirect(url_for('main.index'))

        if not stored_state:
            current_app.logger.error("No stored state in session")
            flash("Authentication failed: Session state not found. Please try again.")
            return redirect(url_for('main.index'))

        if state != stored_state:
            current_app.logger.error(f"State mismatch. Got: {state}, Expected: {stored_state}")
            flash("Authentication failed: State mismatch. Please try again.")
            return redirect(url_for('main.index'))

        # Clear the state from session
        session.pop('oauth_state', None)

        if not code:
            current_app.logger.error("No authorization code received")
            flash("Authentication failed. Please try again.")
            return redirect(url_for('main.index'))

        # Exchange code for tokens
        current_app.logger.info("Exchanging code for tokens")
        tokens = google_auth.exchange_code_for_token(code)

        if 'error' in tokens:
            error_details = tokens.get('error')
            current_app.logger.error(f"Token exchange failed: {error_details}")
            flash(f"Authentication failed: {error_details}")
            return redirect(url_for('main.index'))

        # Get user info using the access token
        current_app.logger.info("Getting user info")
        user_info = google_auth.get_user_info(tokens.get('access_token'))

        if 'error' in user_info:
            error_details = user_info.get('error')
            current_app.logger.error(f"Failed to get user info: {error_details}")
            flash(f"Failed to get user info: {error_details}")
            return redirect(url_for('main.index'))

        # Store user data in session
        current_app.logger.info(f"Authentication successful for user: {user_info.get('email')}")
        google_auth.store_user_session(user_info, tokens)

        return redirect(url_for('main.index'))

    except Exception as e:
        current_app.logger.error(f"Unexpected error in Google callback: {str(e)}", exc_info=True)
        flash(f"An unexpected error occurred during authentication. Please try again.")
        return redirect(url_for('main.index'))

@auth.route('/logout')
def logout():
    """Log out user."""
    session.pop('user', None)
    session.pop('tokens', None)
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

@auth.route('/auth-config')
def auth_config():
    """Display authentication configuration for debugging."""
    # Only show this in development mode
    if not current_app.config.get('RENDER', False):
        config_info = {
            'BASE_URL': current_app.config.get('BASE_URL'),
            'GOOGLE_CLIENT_ID': current_app.config.get('GOOGLE_CLIENT_ID', 'Not set')[:10] + '...' if current_app.config.get('GOOGLE_CLIENT_ID') else 'Not set',
            'REDIRECT_URI': f"{current_app.config.get('BASE_URL')}/auth/google-callback",
        }
        return jsonify(config_info)
    return jsonify({'message': 'Not available in production'})

# Utility function to check if user is logged in
def is_logged_in():
    """Check if user is logged in."""
    return 'user' in session

# Utility function to get current user
def get_current_user():
    """Get current user data."""
    return session.get('user')
