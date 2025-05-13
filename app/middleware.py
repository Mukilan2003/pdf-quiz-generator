from functools import wraps
from flask import session, redirect, url_for, flash, request

def login_required(f):
    """
    Decorator to require login for certain routes.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Please log in to access this page.')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function
