"""
Test Authentication Route
Includes error handling demonstrations
"""

from flask import Blueprint, jsonify, g, request
from ..middleware.auth import token_required, admin_required, super_admin_required
from ..middleware.error_handler import APIError, abort_with_error, validate_request_json

test_auth_bp = Blueprint('test_auth', __name__)

@test_auth_bp.route('/test/public')
def public_route():
    """Public route - no authentication required"""
    return jsonify({
        'success': True,
        'message': 'This is a public route'
    })

@test_auth_bp.route('/test/protected')
@token_required
def protected_route():
    """Protected route - requires valid token"""
    admin = g.current_admin
    return jsonify({
        'success': True,
        'message': 'This is a protected route',
        'admin': {
            'id': admin.id,
            'full_name': admin.full_name,
            'role': admin.role.value
        }
    })

@test_auth_bp.route('/test/admin-only')
@token_required
@admin_required
def admin_only_route():
    """Admin only route"""
    admin = g.current_admin
    return jsonify({
        'success': True,
        'message': 'This route requires admin privileges',
        'admin': {
            'id': admin.id,
            'full_name': admin.full_name,
            'role': admin.role.value
        }
    })

@test_auth_bp.route('/test/super-admin-only')
@token_required
@super_admin_required
def super_admin_only_route():
    """Super admin only route"""
    admin = g.current_admin
    return jsonify({
        'success': True,
        'message': 'This route requires super admin privileges',
        'admin': {
            'id': admin.id,
            'full_name': admin.full_name,
            'role': admin.role.value
        }
    })

# ==================== Error Handling Test Routes ====================

@test_auth_bp.route('/test/error/400')
def test_400_error():
    """Test 400 Bad Request error"""
    raise APIError("This is a test bad request error", status_code=400)

@test_auth_bp.route('/test/error/404')
def test_404_error():
    """Test 404 Not Found error"""
    abort_with_error("Resource not found", status_code=404, resource_id=123)

@test_auth_bp.route('/test/error/500')
def test_500_error():
    """Test 500 Internal Server Error"""
    # This will trigger an unhandled exception
    result = 1 / 0  # Division by zero
    return jsonify({'result': result})

@test_auth_bp.route('/test/error/custom')
def test_custom_error():
    """Test custom API error with payload"""
    raise APIError(
        "Custom error with additional data",
        status_code=422,
        payload={
            'field': 'email',
            'reason': 'Invalid format',
            'suggestion': 'Use format: user@example.com'
        }
    )

@test_auth_bp.route('/test/validation', methods=['POST'])
@validate_request_json(['name', 'email'])
def test_validation():
    """Test request validation decorator"""
    data = request.get_json()
    return jsonify({
        'success': True,
        'message': 'Validation passed',
        'data': data
    })

@test_auth_bp.route('/test/validation-complex', methods=['POST'])
@validate_request_json(['user', 'password', 'email'])
def test_validation_complex():
    """Test validation with multiple required fields"""
    data = request.get_json()
    
    # Additional custom validation
    if len(data['password']) < 6:
        raise APIError(
            "Password must be at least 6 characters",
            status_code=422,
            payload={'field': 'password', 'min_length': 6}
        )
    
    if '@' not in data['email']:
        raise APIError(
            "Invalid email format",
            status_code=422,
            payload={'field': 'email'}
        )
    
    return jsonify({
        'success': True,
        'message': 'Validation passed',
        'data': {
            'user': data['user'],
            'email': data['email']
        }
    })