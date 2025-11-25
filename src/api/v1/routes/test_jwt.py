"""
JWT Testing Routes
Test JWT token generation and validation
"""

from flask import Blueprint, jsonify, request
from ....database.connection import SessionLocal
from ....services.auth_service import AuthService

test_jwt_bp = Blueprint('test_jwt', __name__)
auth_service = AuthService()

@test_jwt_bp.route('/test/jwt/generate/<telegram_id>')
def generate_test_tokens(telegram_id):
    """
    Generate JWT tokens for a Telegram ID (for testing only)
    
    Usage:
        GET /api/v1/test/jwt/generate/123456789
    """
    db = SessionLocal()
    try:
        # Use the authenticate_admin_api method
        result = auth_service.authenticate_admin_api(db, telegram_id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Tokens generated successfully',
                'access_token': result['access_token'],
                'refresh_token': result['refresh_token'],
                'token_type': result['token_type'],
                'expires_in': result['expires_in'],
                'admin': result['admin']
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500
    finally:
        db.close()

@test_jwt_bp.route('/test/jwt/refresh', methods=['POST'])
def refresh_test_token():
    """
    Test token refresh functionality
    
    Usage:
        POST /api/v1/test/jwt/refresh
        Body: {"refresh_token": "your_refresh_token"}
    """
    data = request.get_json()
    refresh_token = data.get('refresh_token')
    
    if not refresh_token:
        return jsonify({
            'success': False,
            'message': 'refresh_token is required'
        }), 400
    
    db = SessionLocal()
    try:
        result = auth_service.refresh_access_token(refresh_token, db)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 401
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500
    finally:
        db.close()

@test_jwt_bp.route('/test/jwt/info')
def jwt_info():
    """
    Display JWT configuration info
    
    Usage:
        GET /api/v1/test/jwt/info
    """
    from ....utils.jwt_helper import jwt_helper
    
    return jsonify({
        'success': True,
        'jwt_config': {
            'algorithm': jwt_helper.algorithm,
            'access_token_expires': f"{jwt_helper.access_token_expires} seconds ({jwt_helper.access_token_expires // 60} minutes)",
            'refresh_token_expires': f"{jwt_helper.refresh_token_expires} seconds ({jwt_helper.refresh_token_expires // 86400} days)",
            'secret_key_set': len(jwt_helper.secret_key) > 0,
            'secret_key_length': len(jwt_helper.secret_key)
        }
    }), 200