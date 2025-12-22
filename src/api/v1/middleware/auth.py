"""
JWT Authentication Middleware
Provides token-based authentication for API endpoints
"""

from functools import wraps
from flask import request, jsonify, g
from ....utils.jwt_helper import jwt_helper
# from ....utils import jwt_helper
from ....database.connection import get_db_session
from ....database.models import Admin

def token_required(f):
    """
    Decorator to require valid JWT token for API endpoints
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                # Format: "Bearer <token>"
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({
                    'success': False,
                    'error': 'invalid_token_format',
                    'message': 'Token format must be: Bearer <token>'
                }), 401
        
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
                'error': 'invalid_token',
                'message': result['message']
            }), 401
        
        # Get admin from database
        db = get_db_session()
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
            
            # Store in Flask g object for access in other decorators
            g.current_admin = admin
            g.token_payload = payload
            
            # Pass admin as kwarg to route function
            kwargs['current_user'] = admin
            
            return f(*args, **kwargs)
            
        finally:
            db.close()
    
    return decorated


def admin_required(f):
    """
    Decorator to require admin or super_admin role
    Must be used after @token_required
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Check if current_admin is in g (set by token_required)
        if not hasattr(g, 'current_admin'):
            return jsonify({
                'success': False,
                'error': 'unauthorized',
                'message': 'Authentication required'
            }), 401
        
        admin = g.current_admin
        
        # Handle both string and Enum types
        role = admin.role.value if hasattr(admin.role, 'value') else admin.role
        
        if role not in ['admin', 'super_admin']:
            return jsonify({
                'success': False,
                'error': 'forbidden',
                'message': 'Admin access required'
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated


def super_admin_required(f):
    """
    Decorator to require super_admin role
    Must be used after @token_required
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Check if current_admin is in g (set by token_required)
        if not hasattr(g, 'current_admin'):
            return jsonify({
                'success': False,
                'error': 'unauthorized',
                'message': 'Authentication required'
            }), 401
        
        admin = g.current_admin
        
        # Handle both string and Enum types
        role = admin.role.value if hasattr(admin.role, 'value') else admin.role
        
        if role != 'super_admin':
            return jsonify({
                'success': False,
                'error': 'forbidden',
                'message': 'Super admin access required'
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated


def optional_auth(f):
    """
    Decorator for optional authentication
    Validates token if provided, but doesn't require it
    Sets g.current_admin if token is valid, otherwise sets to None
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Try to get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                pass  # Invalid format, treat as no token
        
        if not token:
            # No token provided, set current_admin to None and continue
            g.current_admin = None
            g.token_payload = None
            kwargs['current_user'] = None
            return f(*args, **kwargs)
        
        # Token provided, try to verify it
        result = jwt_helper.verify_token(token)
        
        if not result['success']:
            # Invalid token, treat as no authentication
            g.current_admin = None
            g.token_payload = None
            kwargs['current_user'] = None
            return f(*args, **kwargs)
        
        # Valid token, get admin from database
        db = get_db_session()
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
                kwargs['current_user'] = admin
            else:
                g.current_admin = None
                g.token_payload = None
                kwargs['current_user'] = None
            
            return f(*args, **kwargs)
            
        finally:
            db.close()
    
    return decorated