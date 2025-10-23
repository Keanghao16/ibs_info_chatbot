from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from ...database.connection import SessionLocal
from ...database.models import User
from ...services.user_service import UserService
from .auth import any_admin_required, super_admin_required

users_bp = Blueprint('users', __name__)
user_service = UserService()

@users_bp.route('/users')
@any_admin_required
def list_users():
    """List all users with management interface"""
    db = SessionLocal()
    try:
        users = user_service.get_all_users(db)
        return render_template('user/index.html', users=users)
    finally:
        db.close()

@users_bp.route('/users/<int:user_id>')
@any_admin_required
def view_user(user_id):
    """View user details"""
    db = SessionLocal()
    try:
        user = user_service.get_user_by_id(db, user_id)
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('users.list_users'))
        
        # You can add more user details like chat history, messages, etc.
        return render_template('user/user_detail.html', user=user)
    finally:
        db.close()

@users_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@super_admin_required
def remove_user(user_id):
    """Delete user (super admin only)"""
    db = SessionLocal()
    try:
        result = user_service.delete_user(db, user_id)
        
        if result['success']:
            flash(result['message'], 'success')
        else:
            flash(result['message'], 'error')
            
        return redirect(url_for('users.list_users'))
    finally:
        db.close()

@users_bp.route('/users/toggle-status/<int:user_id>', methods=['POST'])
@super_admin_required
def toggle_user_status(user_id):
    """Toggle user active status (super admin only)"""
    db = SessionLocal()
    try:
        result = user_service.toggle_user_status(db, user_id)
        return jsonify(result)
    except Exception as e:
        print(f"Error toggling user status: {e}")
        return jsonify({'success': False, 'message': 'Error updating user status'})
    finally:
        db.close()

@users_bp.route('/users/api/stats')
@any_admin_required
def user_stats():
    """API endpoint for user statistics"""
    db = SessionLocal()
    try:
        users = user_service.get_all_users(db)
        
        stats = {
            "total_users": len(users),
            "active_users": len([u for u in users if u.is_active]),
            "inactive_users": len([u for u in users if not u.is_active]),
            "recent_users": len([u for u in users if u.created_at])  # You can add date filtering
        }
        
        return jsonify({"success": True, "stats": stats})
    finally:
        db.close()

@users_bp.route('/users/search')
@any_admin_required
def search_users():
    """Search users by name, username, or telegram ID"""
    db = SessionLocal()
    try:
        search_term = request.args.get('q', '').lower()
        
        users = user_service.get_all_users(db)
        
        # Filter users based on search term
        filtered_users = [
            u for u in users
            if search_term in (u.full_name or '').lower()
            or search_term in (u.username or '').lower()
            or search_term in str(u.telegram_id)
        ]
        
        return jsonify({
            "success": True,
            "users": [{
                "id": u.id,
                "telegram_id": u.telegram_id,
                "full_name": u.full_name,
                "username": u.username,
                "is_active": u.is_active
            } for u in filtered_users]
        })
    finally:
        db.close()