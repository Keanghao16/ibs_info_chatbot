from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from ...database.connection import SessionLocal
from ...database.models import User
from ...services import UserService  # ✅ Import UserService class
from .auth import any_admin_required, super_admin_required
import asyncio
from telegram import Bot
import os

users_bp = Blueprint('users', __name__)
user_service = UserService()  # ✅ Create service instance

@users_bp.route('/users')
@any_admin_required
def list_users():
    """List all users with management interface"""
    db = SessionLocal()
    try:
        users = user_service.get_all_users(db)  # ✅ Use service method
        return render_template('user/index.html', users=users)
    finally:
        db.close()

@users_bp.route('/users/<user_id>')
@any_admin_required
def view_user(user_id):
    """View user details"""
    db = SessionLocal()
    try:
        user = user_service.get_user_by_id(db, user_id)  # ✅ Use service method
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('users.list_users'))
        
        # Create a user_info dict for the template
        user_info = {
            'id': user.id,
            'telegram_id': user.telegram_id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': user.full_name or f"{user.first_name or ''} {user.last_name or ''}".strip(),
            'photo_url': user.photo_url,
            'is_active': user.is_active,
            'last_activity': user.last_activity,
            'created_at': user.created_at
        }
        
        return render_template('user/view.html', user_info=user_info)
    finally:
        db.close()

@users_bp.route('/users/delete/<user_id>', methods=['POST'])
@super_admin_required
def remove_user(user_id):
    """Delete user (super admin only)"""
    db = SessionLocal()
    try:
        result = user_service.delete_user(db, user_id)  # ✅ Use service method
        
        if result['success']:
            flash(result['message'], 'success')
        else:
            flash(result['message'], 'error')
            
        return redirect(url_for('users.list_users'))
    finally:
        db.close()

@users_bp.route('/users/toggle-status/<user_id>', methods=['POST'])
@super_admin_required
def toggle_status(user_id):
    """Toggle user active status (super admin only)"""
    db = SessionLocal()
    try:
        result = user_service.toggle_user_status(db, user_id)  # ✅ Use service method
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
        users = user_service.get_all_users(db)  # ✅ Use service method
        
        stats = {
            "total_users": len(users),
            "active_users": len([u for u in users if u.is_active]),
            "inactive_users": len([u for u in users if not u.is_active]),
            "recent_users": len([u for u in users if u.created_at])
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
        
        users = user_service.get_all_users(db)  # ✅ Use service method
        
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

@users_bp.route('/users/send-message', methods=['POST'])
@any_admin_required
def send_message_to_user():
    """Send message to user via Telegram bot"""
    try:
        data = request.get_json()
        telegram_id = data.get('telegram_id')
        message = data.get('message')
        
        if not telegram_id or not message:
            return jsonify({
                'success': False,
                'message': 'Missing telegram_id or message'
            })
        
        # Get bot token from environment
        bot_token = os.getenv('BOT_TOKEN') or os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            return jsonify({
                'success': False,
                'message': 'Bot token not configured'
            })
        
        # Send message via Telegram bot
        async def send_telegram_message():
            bot = Bot(token=bot_token)
            admin_name = session.get('admin_info', {}).get('full_name', 'Admin')
            formatted_message = f"📩 *Message from {admin_name}*\n\n{message}"
            
            await bot.send_message(
                chat_id=telegram_id,
                text=formatted_message,
                parse_mode='Markdown'
            )
        
        # Run async function
        asyncio.run(send_telegram_message())
        
        return jsonify({
            'success': True,
            'message': 'Message sent successfully'
        })
        
    except Exception as e:
        print(f"Error sending message: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to send message: {str(e)}'
        })

@users_bp.route('/users/promote/<user_id>', methods=['POST'])
@super_admin_required
def promote_to_admin(user_id):
    """Promote user to admin (super admin only)"""
    db = SessionLocal()
    try:
        user = user_service.get_user_by_id(db, user_id)  # ✅ Use service method
        if not user:
            return jsonify({'success': False, 'message': 'User not found'})
        
        # Get admin data from request
        data = request.get_json()
        role = data.get('role', 'admin')
        division = data.get('division', 'Support')
        
        # Validate role
        if role not in ['admin', 'super_admin']:
            return jsonify({'success': False, 'message': 'Invalid role specified'})
        
        # Get current admin ID from session
        current_admin_id = session.get('admin_info', {}).get('id')
        
        # Promote user using service method
        from ...database.models import AdminRole
        admin_role = AdminRole.super_admin if role == 'super_admin' else AdminRole.admin
        
        result = user_service.promote_user_to_admin(  # ✅ Use service method
            db=db,
            telegram_id=user.telegram_id,
            promoted_by_admin_id=current_admin_id,
            role=admin_role,
            division=division if role == 'admin' else None,
            is_available=True if role == 'admin' else None
        )
        
        if not result['success']:
            return jsonify(result)
        
        admin = result['admin']
        role_name = 'Super Administrator' if role == 'super_admin' else 'Admin/Agent'
        
        return jsonify({
            'success': True,
            'message': f'User promoted to {role_name} successfully',
            'admin': {
                'id': admin.id,
                'full_name': admin.full_name,
                'role': admin.role.value
            }
        })
        
    except Exception as e:
        print(f"Error promoting user: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)})
    finally:
        db.close()