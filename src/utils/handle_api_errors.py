from functools import wraps
from flask import flash, redirect, url_for

def handle_api_errors(f):
    """Decorator to handle common API errors"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')
            return redirect(url_for('dashboard.index'))
    
    return decorated_function