from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
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
        auth_url = google_auth.get_google_auth_url()
        return redirect(auth_url)
    except Exception as e:
        flash(f"Error initiating Google login: {str(e)}")
        return redirect(url_for('main.index'))

@auth.route('/google-callback')
def google_callback():
    """Handle Google OAuth callback."""
    # Get the authorization code from the request
    code = request.args.get('code')
    state = request.args.get('state')

    # Verify state parameter to prevent CSRF
    stored_state = session.get('oauth_state')
    if not state or not stored_state or state != stored_state:
        flash("Invalid state parameter. Please try again.")
        return redirect(url_for('main.index'))

    # Clear the state from session
    session.pop('oauth_state', None)

    if not code:
        flash("Authentication failed. Please try again.")
        return redirect(url_for('main.index'))

    # Exchange code for tokens
    tokens = google_auth.exchange_code_for_token(code)

    if 'error' in tokens:
        flash(f"Authentication failed: {tokens.get('error')}")
        return redirect(url_for('main.index'))

    # Get user info using the access token
    user_info = google_auth.get_user_info(tokens.get('access_token'))

    if 'error' in user_info:
        flash(f"Failed to get user info: {user_info.get('error')}")
        return redirect(url_for('main.index'))

    # Store user data in session
    google_auth.store_user_session(user_info, tokens)

    return redirect(url_for('main.index'))

@auth.route('/logout')
def logout():
    """Log out user."""
    session.pop('user', None)
    session.pop('tokens', None)
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

# Utility function to check if user is logged in
def is_logged_in():
    """Check if user is logged in."""
    return 'user' in session

# Utility function to get current user
def get_current_user():
    """Get current user data."""
    return session.get('user')
