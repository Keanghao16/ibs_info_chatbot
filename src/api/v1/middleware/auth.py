"""
JWT Authentication Middleware
Provides token-based authentication for API endpoints
"""

from functools import wraps
from flask import request, jsonify, g
from ....utils.jwt_helper import jwt_helper
from ....database.connection import SessionLocal
from ....database.models import Admin, AdminRole

def token_required(f):
    """
    Decorator to require valid JWT token for API endpoints
    
    Usage:
        @token_required
        def protected_route():
            # Access current admin via g.current_admin
            pass
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header:
            token = jwt_helper.extract_token_from_header(auth_header)
        
        if not token:
            return jsonify({
                'success': False,
                'error': 'missing_token',
                'message': 'Authentication token is missing'
            }), 401
        
        # Verify token
        result = jwt_helper.verify_token(token)
        
        if not result['success']:
            return jsonify({
                'success': False,
                'error': result['error'],
                'message': result['message']
            }), 401
        
        # Get admin from database
        db = SessionLocal()
        try:
            payload = result['payload']
            admin_id = payload.get('admin_id')
            
            admin = db.query(Admin).filter(
                Admin.id == admin_id,
                Admin.is_active == True
            ).first()
            
            if not admin:
                return jsonify({
                    'success': False,
                    'error': 'admin_not_found',
                    'message': 'Admin account not found or inactive'
                }), 401
            
            # Store admin in Flask's g object for access in route
            g.current_admin = admin
            g.token_payload = payload
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'authentication_error',
                'message': str(e)
            }), 500
        finally:
            db.close()
        
        return f(*args, **kwargs)
    
    return decorated


def admin_required(f):
    """
    Decorator to require admin or super_admin role
    Must be used after @token_required
    
    Usage:
        @token_required
        @admin_required
        def admin_only_route():
            pass
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if not hasattr(g, 'current_admin'):
            return jsonify({
                'success': False,
                'error': 'authentication_required',
                'message': 'Authentication required'
            }), 401
        
        admin = g.current_admin
        
        if admin.role not in [AdminRole.admin, AdminRole.super_admin]:
            return jsonify({
                'success': False,
                'error': 'insufficient_permissions',
                'message': 'Admin privileges required'
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated


def super_admin_required(f):
    """
    Decorator to require super_admin role
    Must be used after @token_required
    
    Usage:
        @token_required
        @super_admin_required
        def super_admin_only_route():
            pass
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if not hasattr(g, 'current_admin'):
            return jsonify({
                'success': False,
                'error': 'authentication_required',
                'message': 'Authentication required'
            }), 401
        
        admin = g.current_admin
        
        if admin.role != AdminRole.super_admin:
            return jsonify({
                'success': False,
                'error': 'insufficient_permissions',
                'message': 'Super Admin privileges required'
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated


def optional_auth(f):
    """
    Decorator for optional authentication
    If token is provided and valid, sets g.current_admin
    If token is missing or invalid, continues without authentication
    
    Usage:
        @optional_auth
        def public_route():
            if hasattr(g, 'current_admin'):
                # User is authenticated
                pass
            else:
                # User is not authenticated
                pass
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header:
            token = jwt_helper.extract_token_from_header(auth_header)
        
        if token:
            # Verify token
            result = jwt_helper.verify_token(token)
            
            if result['success']:
                # Get admin from database
                db = SessionLocal()
                try:
                    payload = result['payload']
                    admin_id = payload.get('admin_id')
                    
                    admin = db.query(Admin).filter(
                        Admin.id == admin_id,
                        Admin.is_active == True
                    ).first()
                    
                    if admin:
                        g.current_admin = admin
                        g.token_payload = payload
                
                finally:
                    db.close()
        
        return f(*args, **kwargs)
    
    return decorated