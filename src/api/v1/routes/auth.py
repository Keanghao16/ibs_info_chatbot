"""
API Authentication Routes
JWT-based authentication for REST API
"""

from flask import Blueprint, request, jsonify, g
from ....database.connection import get_db_session
from ....services.auth_service import AuthService
from ..middleware.auth import token_required, optional_auth
from ..middleware.error_handler import validate_request_json, APIError
from ..schemas.response_schema import ResponseBuilder

auth_api_bp = Blueprint('auth_api', __name__)
auth_service = AuthService()


@auth_api_bp.route('/auth/login', methods=['POST'])
@validate_request_json(['telegram_id'])
def login():
    """
    Admin login with Telegram ID (returns JWT tokens)
    
    Request Body:
        {
            "telegram_id": "123456789"
        }
    
    Response:
        {
            "success": true,
            "message": "Login successful",
            "data": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                "token_type": "Bearer",
                "expires_in": 3600,
                "admin": {
                    "id": 1,
                    "telegram_id": "123456789",
                    "full_name": "John Doe",
                    "role": "super_admin",
                    "is_active": true
                }
            }
        }
    """
    db = get_db_session()
    try:
        data = request.get_json()
        telegram_id = data['telegram_id']
        
        # Use existing auth service method for API login
        result = auth_service.authenticate_admin_api(db, telegram_id)
        
        if result['success']:
            return ResponseBuilder.success(
                data={
                    'access_token': result['access_token'],
                    'refresh_token': result['refresh_token'],
                    'token_type': result['token_type'],
                    'expires_in': result['expires_in'],
                    'admin': result['admin']
                },
                message='Login successful'
            )
        else:
            return ResponseBuilder.unauthorized(result['message'])
    
    except Exception as e:
        return ResponseBuilder.error(
            message=f"Login failed: {str(e)}",
            status_code=500
        )
    finally:
        db.close()


@auth_api_bp.route('/auth/refresh', methods=['POST'])
@validate_request_json(['refresh_token'])
def refresh_token():
    """
    Refresh access token using refresh token
    
    Request Body:
        {
            "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
        }
    
    Response:
        {
            "success": true,
            "message": "Token refreshed",
            "data": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                "token_type": "Bearer",
                "expires_in": 3600
            }
        }
    """
    db = get_db_session()
    try:
        data = request.get_json()
        refresh_token = data['refresh_token']
        
        result = auth_service.refresh_access_token(refresh_token, db)
        
        if result['success']:
            return ResponseBuilder.success(
                data={
                    'access_token': result['access_token'],
                    'token_type': result['token_type'],
                    'expires_in': result['expires_in']
                },
                message='Token refreshed successfully'
            )
        else:
            return ResponseBuilder.unauthorized(result['message'])
    
    except Exception as e:
        return ResponseBuilder.error(
            message=f"Token refresh failed: {str(e)}",
            status_code=500
        )
    finally:
        db.close()


@auth_api_bp.route('/auth/me', methods=['GET'])
@token_required
def get_current_admin(current_user):  #  Add parameter
    """Get current authenticated admin information"""
    admin = g.current_admin
    
    return ResponseBuilder.success(
        data={
            'id': admin.id,
            'telegram_id': str(admin.telegram_id),
            'telegram_username': admin.telegram_username,
            'full_name': admin.full_name,
            'role': admin.role.value if hasattr(admin.role, 'value') else admin.role,
            'is_active': admin.is_active,
            'is_available': admin.is_available,
            'division': admin.division,
            'created_at': admin.created_at.isoformat() if admin.created_at else None,
            'last_login': admin.last_login.isoformat() if admin.last_login else None
        },
        message='Admin info retrieved successfully'
    )


@auth_api_bp.route('/auth/logout', methods=['POST'])
@token_required
def logout(current_user):  #  Add parameter
    """
    Logout (client should discard tokens)
    
    Headers:
        Authorization: Bearer <access_token>
    
    Response:
        {
            "success": true,
            "message": "Logout successful"
        }
    """
    admin = g.current_admin
    
    return ResponseBuilder.success(
        message=f"Logout successful. Goodbye {admin.full_name}!"
    )


@auth_api_bp.route('/auth/update-profile', methods=['PUT'])
@token_required
@validate_request_json(['full_name'])
def update_profile(current_user):  #  Add parameter
    """
    Update admin profile information
    
    Headers:
        Authorization: Bearer <access_token>
    
    Request Body:
        {
            "full_name": "John Doe Updated",
            "division": "IT Department"  // Optional, only for regular admins
        }
    
    Response:
        {
            "success": true,
            "message": "Profile updated successfully",
            "data": {
                "id": 1,
                "full_name": "John Doe Updated",
                "division": "IT Department",
                ...
            }
        }
    """
    db = get_db_session()
    try:
        admin = g.current_admin
        data = request.get_json()
        
        full_name = data['full_name']
        division = data.get('division')
        
        result = auth_service.update_admin_profile(
            db, 
            admin.id, 
            full_name, 
            division
        )
        
        if result['success']:
            return ResponseBuilder.updated(
                data=result['admin'],
                message='Profile updated successfully'
            )
        else:
            return ResponseBuilder.bad_request(result['message'])
    
    except Exception as e:
        return ResponseBuilder.error(
            message=f"Profile update failed: {str(e)}",
            status_code=500
        )
    finally:
        db.close()


@auth_api_bp.route('/auth/toggle-availability', methods=['POST'])
@token_required
def toggle_availability(current_user):
    """Toggle admin availability for chat assignment (admins only)"""
    db = get_db_session()
    try:
        admin = g.current_admin
        
        result = auth_service.toggle_admin_availability(db, admin.id)
        
        if result['success']:
            return ResponseBuilder.success(
                data={
                    'is_available': result['is_available'],
                    'admin': result['admin']
                },
                message=result['message']
            )
        else:
            return ResponseBuilder.bad_request(result['message'])  #  FIXED
    
    except Exception as e:
        return ResponseBuilder.error(
            message=f"Failed to toggle availability: {str(e)}",
            status_code=500
        )
    finally:
        db.close()


@auth_api_bp.route('/auth/verify', methods=['GET'])
@token_required
def verify_token(current_user):  #  Add parameter
    """
    Verify if current token is valid
    
    Headers:
        Authorization: Bearer <access_token>
    
    Response:
        {
            "success": true,
            "message": "Token is valid",
            "data": {
                "admin_id": 1,
                "role": "super_admin",
                "token_type": "access",
                "expires_at": "2025-11-11T11:30:00"
            }
        }
    """
    admin = g.current_admin
    payload = g.token_payload
    
    return ResponseBuilder.success(
        data={
            'valid': True,
            'admin_id': admin.id,
            'role': admin.role.value if hasattr(admin.role, 'value') else admin.role,
            'token_type': payload.get('token_type', 'access'),
            'expires_at': payload.get('exp')
        },
        message='Token is valid'
    )


@auth_api_bp.route('/auth/telegram-callback', methods=['POST'])
def telegram_callback():
    """
    Handle Telegram Login Widget callback (for web-based login)
    """
    db = get_db_session()
    try:
        telegram_data = request.get_json()
        
        print(f"🔍 Telegram callback received: {telegram_data}")  # Debug
        
        if not telegram_data.get('id'):
            raise APIError("Telegram ID is required", status_code=400)
        
        # Use existing Telegram authentication method
        result = auth_service.authenticate_admin_telegram(db, telegram_data)
        
        print(f"🔍 Auth result: {result}")  # Debug
        
        if result['success']:
            #  FIXED: Return proper API tokens
            return ResponseBuilder.success(
                data={
                    'access_token': result.get('access_token') or result.get('token'),  # Handle both formats
                    'refresh_token': result.get('refresh_token'),
                    'token_type': result.get('token_type', 'Bearer'),
                    'expires_in': result.get('expires_in', 3600),
                    'admin': result['admin']
                },
                message='Login successful'
            )
        else:
            return ResponseBuilder.unauthorized(result['message'])
    
    except Exception as e:
        print(f"❌ Telegram login error: {str(e)}")
        import traceback
        traceback.print_exc()
        return ResponseBuilder.error(
            message=f"Telegram login failed: {str(e)}",
            status_code=500
        )
    finally:
        db.close()


# Add this test route at the end of the file
@auth_api_bp.route('/auth/test', methods=['GET'])
def test_auth_route():
    """Test route to verify auth blueprint is working"""
    return jsonify({
        'success': True,
        'message': 'Auth blueprint is working!',
        'available_routes': [
            '/auth/login',
            '/auth/refresh',
            '/auth/me',
            '/auth/telegram-callback',
            '/auth/test'
        ]
    })