"""
Users API Routes
Handles all user-related API endpoints
"""

from flask import Blueprint, request, jsonify
from ..middleware.auth import token_required, admin_required
from ..schemas import (
    UserResponseSchema,
    UserListResponseSchema,
    UserCreateSchema,
    UserUpdateSchema,
    UserStatsSchema,
    success_response,
    error_response,
    paginated_response,
    created_response,
    updated_response,
    deleted_response,
    not_found_response,
    validation_error_response
)
from ....services.user_service import UserService
from ....database.connection import get_db_session
from marshmallow import ValidationError

# Create blueprint
users_api_bp = Blueprint('users_api', __name__)

# Initialize schemas
user_response_schema = UserResponseSchema()
user_list_schema = UserListResponseSchema(many=True)
user_create_schema = UserCreateSchema()
user_update_schema = UserUpdateSchema()
user_stats_schema = UserStatsSchema()


@users_api_bp.route('/users', methods=['GET'])
@token_required
@admin_required
def list_users(current_user):
    """Get paginated list of users"""
    from contextlib import closing
    
    with closing(get_db_session()) as db:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        
        result = UserService.get_all_users(db=db, page=page, per_page=per_page)
        users_data = user_list_schema.dump(result['users'])
        
        return paginated_response(
            data=users_data,
            page=result['page'],
            per_page=result['per_page'],
            total=result['total'],
            message=f"Retrieved {len(users_data)} users"
        )


@users_api_bp.route('/users/<string:user_id>', methods=['GET'])  # ✅ Changed to string
@token_required
@admin_required
def get_user(current_user, user_id):
    """Get single user by ID (UUID)"""
    db = get_db_session()
    try:
        user = UserService.get_user_by_id(db, user_id)
        
        if not user:
            return not_found_response('User')
        
        user_data = user_response_schema.dump(user)
        
        return success_response(
            data=user_data,
            message="User retrieved successfully"
        )
    except Exception as e:
        return error_response(str(e), 500)
    finally:
        db.close()


@users_api_bp.route('/users', methods=['POST'])
@token_required
@admin_required
def create_user(current_user):
    """Create new user"""
    db = get_db_session()
    try:
        try:
            user_data = user_create_schema.load(request.json)
        except ValidationError as err:
            return validation_error_response(err.messages)
        
        # Check if telegram_id already exists
        existing_user = UserService.get_user_by_telegram_id(db, user_data['telegram_id'])
        if existing_user:
            return error_response(
                "User with this Telegram ID already exists",
                400
            )
        
        # Create user
        new_user = UserService.create_user(db, user_data)
        
        user_response = user_response_schema.dump(new_user)
        
        return created_response(
            data=user_response,
            message="User created successfully"
        )
        
    except Exception as e:
        db.rollback()
        return error_response(str(e), 500)
    finally:
        db.close()


@users_api_bp.route('/users/<string:user_id>', methods=['PUT'])  # ✅ Changed to string
@token_required
@admin_required
def update_user(current_user, user_id):
    """Update user information"""
    db = get_db_session()
    try:
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return not_found_response('User')
        
        try:
            update_data = user_update_schema.load(request.json)
        except ValidationError as err:
            return validation_error_response(err.messages)
        
        updated_user = UserService.update_user(db, user_id, update_data)
        user_response = user_response_schema.dump(updated_user)
        
        return updated_response(
            data=user_response,
            message="User updated successfully"
        )
        
    except Exception as e:
        db.rollback()
        return error_response(str(e), 500)
    finally:
        db.close()


@users_api_bp.route('/users/<string:user_id>', methods=['DELETE'])  # ✅ Changed to string
@token_required
@admin_required
def delete_user(current_user, user_id):
    """Delete user"""
    db = get_db_session()
    try:
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return not_found_response('User')
        
        UserService.delete_user(db, user_id)
        
        return deleted_response(message="User deleted successfully")
        
    except Exception as e:
        db.rollback()
        return error_response(str(e), 500)
    finally:
        db.close()


@users_api_bp.route('/users/stats', methods=['GET'])
@token_required
@admin_required
def get_user_stats(current_user):
    """Get user statistics"""
    db = get_db_session()
    try:
        stats = UserService.get_user_statistics(db)
        stats_data = user_stats_schema.dump(stats)
        
        return success_response(
            data=stats_data,
            message="User statistics retrieved successfully"
        )
        
    except Exception as e:
        return error_response(str(e), 500)
    finally:
        db.close()