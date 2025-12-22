"""
Web Authentication Decorators
Authentication and authorization decorators for web routes
"""

from functools import wraps
from flask import session, redirect, url_for, flash, request

def any_admin_required(f):
    """
    Decorator to require any admin (admin or super_admin) to be logged in
    
    Checks for:
    - access_token in session (JWT token from API login)
    - admin info in session
    - admin is active
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user has access token (from API login)
        if 'access_token' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('auth.login'))
        
        # Check if admin info exists in session
        if 'admin' not in session:
            flash('Session expired. Please login again.', 'error')
            session.clear()
            return redirect(url_for('auth.login'))
        
        admin = session.get('admin', {})
        
        # Check if admin is active
        if not admin.get('is_active', False):
            flash('Your account is inactive. Please contact administrator.', 'error')
            session.clear()
            return redirect(url_for('auth.login'))
        
        # Check if admin has valid role
        role = admin.get('role')
        if role not in ['admin', 'super_admin']:
            flash('Admin access required', 'error')
            return redirect(url_for('auth.login'))
        
        return f(*args, **kwargs)
    
    return decorated_function

def super_admin_required(f):
    """
    Decorator to require super admin to be logged in
    
    Checks for:
    - All requirements from any_admin_required
    - Role must be 'super_admin'
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # First check basic admin requirements
        if 'access_token' not in session or 'admin' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('auth.login'))
        
        admin = session.get('admin', {})
        
        if not admin.get('is_active', False):
            flash('Your account is inactive. Please contact administrator.', 'error')
            session.clear()
            return redirect(url_for('auth.login'))
        
        # Check for super admin role specifically
        if admin.get('role') != 'super_admin':
            flash('Super admin access required for this action', 'error')
            return redirect(url_for('dashboard.index'))
        
        return f(*args, **kwargs)
    
    return decorated_function

def optional_auth(f):
    """
    Decorator for optional authentication
    Sets session info if available, but doesn't require login
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Just pass through - session info will be available if logged in
        return f(*args, **kwargs)
    
    return decorated_function

def require_auth():
    """
    Helper function to check authentication inline (not a decorator)
    Returns redirect response if auth fails, None if success
    """
    if 'access_token' not in session or 'admin' not in session:
        flash('Please login to access this page', 'error')
        return redirect(url_for('auth.login'))
    
    admin = session.get('admin', {})
    if not admin.get('is_active'):
        flash('Your account is inactive', 'error')
        session.clear()
        return redirect(url_for('auth.login'))
    
    return None

def require_super_admin():
    """
    Helper function to check super admin access inline (not a decorator)
    Returns redirect response if auth fails, None if success
    """
    auth_check = require_auth()
    if auth_check:
        return auth_check
    
    admin = session.get('admin', {})
    if admin.get('role') != 'super_admin':
        flash('Super admin access required', 'error')
        return redirect(url_for('dashboard.index'))
    
    return None