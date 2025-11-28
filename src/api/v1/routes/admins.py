"""
Admins API Routes
Handles all admin-related API endpoints
"""

from flask import Blueprint, request, jsonify, g
from ..middleware.auth import token_required, super_admin_required
from ..schemas import (
    AdminResponseSchema,
    AdminListResponseSchema,
    AdminCreateSchema,
    AdminUpdateSchema,
    # AdminPasswordUpdateSchema,  # ❌ Remove if not using
    AdminStatsSchema,
    success_response,
    error_response,
    paginated_response,
    created_response,
    updated_response,
    deleted_response,
    not_found_response,
    validation_error_response
)
from ....services.admin_service import AdminService
from ....database.connection import get_db_session
from marshmallow import ValidationError
import traceback

# Create blueprint
admins_api_bp = Blueprint('admins_api', __name__)

# Initialize schemas
admin_response_schema = AdminResponseSchema()
admin_list_schema = AdminListResponseSchema(many=True)
admin_create_schema = AdminCreateSchema()
admin_update_schema = AdminUpdateSchema()
# admin_password_schema = AdminPasswordUpdateSchema()  # ❌ Remove if not using
admin_stats_schema = AdminStatsSchema()


@admins_api_bp.route('/admins', methods=['GET'])
@token_required
def list_admins(current_user):
    """Get paginated list of admins
    
    Query Parameters:
        - page (int): Page number (default: 1)
        - per_page (int): Items per page (default: 10)
        - search (str): Search by username or email
        - role (str): Filter by role (admin/super_admin)
        - is_active (bool): Filter by active status
        - is_available (bool): Filter by availability
    """
    db = get_db_session()
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        search = request.args.get('search', '').strip() or None
        role = request.args.get('role')
        
        # ✅ Fix boolean parsing
        is_active = None
        if request.args.get('is_active'):
            is_active_str = request.args.get('is_active').lower()
            is_active = is_active_str in ['true', '1', 'yes']
        
        is_available = None
        if request.args.get('is_available'):
            is_available_str = request.args.get('is_available').lower()
            is_available = is_available_str in ['true', '1', 'yes']
        
        # Get admins
        result = AdminService.get_all_admins(
            db=db,
            page=page,
            per_page=per_page,
            search=search,
            role=role,
            is_active=is_active,
            is_available=is_available
        )
        
        # Serialize data
        admins_data = admin_list_schema.dump(result['admins'])
        
        return paginated_response(
            data=admins_data,
            page=result['page'],
            per_page=result['per_page'],
            total=result['total'],
            message=f"Retrieved {len(admins_data)} admins"
        )
        
    except Exception as e:
        print(f"Error in list_admins: {str(e)}")
        print(traceback.format_exc())
        return error_response(str(e), 500)
    finally:
        db.close()


@admins_api_bp.route('/admins/<string:admin_id>', methods=['GET'])  # ✅ Changed to string
@token_required
def get_admin(current_user, admin_id):
    """Get single admin by ID (UUID)"""
    db = get_db_session()
    try:
        admin = AdminService.get_admin_by_id(db, admin_id)
        
        if not admin:
            return not_found_response('Admin')
        
        admin_data = admin_response_schema.dump(admin)
        
        return success_response(
            data=admin_data,
            message="Admin retrieved successfully"
        )
        
    except Exception as e:
        return error_response(str(e), 500)
    finally:
        db.close()


@admins_api_bp.route('/admins', methods=['POST'])
@token_required
@super_admin_required
def create_admin(current_user):
    """
    Create new admin (Super Admin only)
    
    Request Body:
        {
            "telegram_id": "987654321",
            "username": "new_admin_username",  // Optional
            "full_name": "New Admin Name",
            "role": "admin",  // or "super_admin"
            "division": "Support"  // Optional, only for 'admin' role
        }
    """
    db = get_db_session()
    try:
        try:
            admin_data = admin_create_schema.load(request.json)
        except ValidationError as err:
            return validation_error_response(err.messages)
        
        # ✅ Check if telegram_id already exists
        existing_admin = AdminService.get_admin_by_telegram_id(db, admin_data['telegram_id'])
        if existing_admin:
            return error_response(
                "Admin with this Telegram ID already exists",
                400
            )
        
        # ✅ Create admin
        new_admin = AdminService.create_admin(db, admin_data)
        admin_response = admin_response_schema.dump(new_admin)
        
        return created_response(
            data=admin_response,
            message="Admin created successfully"
        )
        
    except Exception as e:
        db.rollback()
        print(f"Error creating admin: {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(str(e), 500)
    finally:
        db.close()


@admins_api_bp.route('/admins/<string:admin_id>', methods=['PUT'])  # ✅ Changed to string
@token_required
def update_admin(current_user, admin_id):
    """Update admin information"""
    db = get_db_session()
    try:
        # Check permissions
        current_admin_role = current_user.role.value if hasattr(current_user.role, 'value') else current_user.role
        
        if current_admin_role != 'super_admin' and current_user.id != admin_id:
            return error_response("You can only update your own profile", 403)
        
        admin = AdminService.get_admin_by_id(db, admin_id)
        if not admin:
            return not_found_response('Admin')
        
        try:
            update_data = admin_update_schema.load(request.json)
        except ValidationError as err:
            return validation_error_response(err.messages)
        
        updated_admin = AdminService.update_admin(db, admin_id, update_data)
        admin_response = admin_response_schema.dump(updated_admin)
        
        return updated_response(
            data=admin_response,
            message="Admin updated successfully"
        )
        
    except Exception as e:
        db.rollback()
        return error_response(str(e), 500)
    finally:
        db.close()


@admins_api_bp.route('/admins/<string:admin_id>', methods=['DELETE'])  # ✅ Changed to string
@token_required
@super_admin_required
def delete_admin(current_user, admin_id):
    """Delete admin (Super Admin only)"""
    db = get_db_session()
    try:
        # Prevent self-deletion
        if current_user.id == admin_id:
            return error_response("You cannot delete your own account", 400)
        
        admin = AdminService.get_admin_by_id(db, admin_id)
        if not admin:
            return not_found_response('Admin')
        
        AdminService.delete_admin(db, admin_id)
        
        return deleted_response(message="Admin deleted successfully")
        
    except Exception as e:
        db.rollback()
        return error_response(str(e), 500)
    finally:
        db.close()


@admins_api_bp.route('/admins/<string:admin_id>/toggle-availability', methods=['PUT'])  # ✅ Changed to string
@token_required
def toggle_admin_availability(current_user, admin_id):
    """Toggle admin availability"""
    db = get_db_session()
    try:
        # Check if admin exists
        admin = AdminService.get_admin_by_id(db, admin_id)
        if not admin:
            return not_found_response('Admin')
        
        # Check permission (can only toggle own availability or be super_admin)
        current_role = current_user.role.value if hasattr(current_user.role, 'value') else current_user.role
        
        if current_user.id != admin_id and current_role != 'super_admin':
            return error_response('You can only toggle your own availability', 403)
        
        updated_admin = AdminService.toggle_availability(db, admin_id)
        admin_response = admin_response_schema.dump(updated_admin)
        
        return updated_response(
            data=admin_response,
            message=f"Admin availability toggled to {updated_admin.is_available}"
        )
        
    except Exception as e:
        db.rollback()
        return error_response(str(e), 500)
    finally:
        db.close()


@admins_api_bp.route('/admins/stats', methods=['GET'])
@token_required
def get_admin_stats(current_user):
    """Get admin statistics"""
    db = get_db_session()
    try:
        stats = AdminService.get_admin_statistics(db)
        stats_data = admin_stats_schema.dump(stats)
        
        return success_response(
            data=stats_data,
            message="Admin statistics retrieved successfully"
        )
        
    except Exception as e:
        return error_response(str(e), 500)
    finally:
        db.close()