from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from ...database.connection import SessionLocal
from ...services import AdminService, UserService  # ✅ Add UserService
from .auth import super_admin_required, any_admin_required
from ...database.models import Admin, AdminRole
from ...utils import Helpers

admin_bp = Blueprint('admin', __name__)
admin_service = AdminService()
user_service = UserService()  # ✅ Create UserService instance

@admin_bp.route('/administrators')
@super_admin_required
def manage_admins():
    """List all administrators with pagination"""
    db = SessionLocal()
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        admins = admin_service.get_all_admins(db)
        
        # Apply pagination
        paginated_admins = Helpers.paginate(admins, page, per_page)
        
        # Calculate total pages
        total_admins = len(admins)
        total_pages = (total_admins + per_page - 1) // per_page
        
        return render_template('admin/index.html', 
                             admins=paginated_admins,
                             page=page,
                             per_page=per_page,
                             total_admins=total_admins,
                             total_pages=total_pages)
    finally:
        db.close()

@admin_bp.route('/admin/create-admin-telegram', methods=['POST'])
@super_admin_required
def create_admin_telegram():
    """Create new admin using Telegram ID"""
    db = SessionLocal()
    try:
        telegram_id = request.form.get('telegram_id')
        full_name = request.form.get('full_name')
        role = request.form.get('role', 'admin')
        division = request.form.get('division')
        
        # Validate inputs
        if not telegram_id or not full_name:
            flash('Telegram ID and Full Name are required.', 'error')
            return redirect(url_for('admin.manage_admins'))
        
        # Create admin using service
        result = admin_service.create_admin(
            db=db,
            telegram_id=telegram_id,
            full_name=full_name,
            role=role,
            division=division
        )
        
        if result['success']:
            flash(result['message'], 'success')
        else:
            flash(result['message'], 'error')
            
    except Exception as e:
        print(f"Error creating admin: {e}")
        import traceback
        traceback.print_exc()
        flash('Error creating admin account.', 'error')
    finally:
        db.close()
    
    return redirect(url_for('admin.manage_admins'))

@admin_bp.route('/admin/toggle-admin-status/<string:admin_id>', methods=['POST'])
@super_admin_required
def toggle_admin_status(admin_id):
    """Toggle admin active status"""
    db = SessionLocal()
    try:
        current_admin_id = session['admin_info']['id']
        result = admin_service.toggle_admin_status(db, admin_id, current_admin_id)
        return jsonify(result)
    except Exception as e:
        print(f"Error toggling admin status: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Error updating admin status'})
    finally:
        db.close()

@admin_bp.route('/admin/toggle-availability', methods=['POST'])
@any_admin_required
def toggle_availability():
    """Toggle admin availability for taking new chats"""
    db = SessionLocal()
    try:
        current_admin_id = session['admin_info']['id']
        result = admin_service.toggle_admin_availability(db, current_admin_id)
        
        if result['success']:
            # Update session
            session['admin_info']['is_available'] = result['is_available']
            session.modified = True
        
        return jsonify(result)
    except Exception as e:
        print(f"Error toggling availability: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Error updating availability'})
    finally:
        db.close()

@admin_bp.route('/administrators/<string:admin_id>')
@super_admin_required
def view_admin_profile(admin_id):
    """View another admin's profile"""
    db = SessionLocal()
    try:
        admin_info = admin_service.get_admin_info(db, admin_id)
        
        if not admin_info:
            flash('Admin not found.', 'error')
            return redirect(url_for('admin.manage_admins'))
        
        # Flag to indicate this is viewing another admin's profile
        is_viewing_other = True
        
        return render_template('admin/view.html', 
                             admin_info=admin_info,
                             is_viewing_other=is_viewing_other)
    finally:
        db.close()

@admin_bp.route('/administrators/<string:admin_id>/edit', methods=['GET', 'POST'])
@super_admin_required
def edit_admin(admin_id):
    """Edit admin profile"""
    db = SessionLocal()
    try:
        if request.method == 'POST':
            # Get form data
            full_name = request.form.get('full_name', '').strip()
            division = request.form.get('division', '').strip()
            role = request.form.get('role')
            
            # Update admin using service
            result = admin_service.update_admin_profile(
                db=db,
                admin_id=admin_id,
                full_name=full_name,
                division=division,
                role=role
            )
            
            if result['success']:
                flash(result['message'], 'success')
                return redirect(url_for('admin.view_admin_profile', admin_id=admin_id))
            else:
                flash(result['message'], 'error')
        
        # GET request - show edit form
        admin_info = admin_service.get_admin_info(db, admin_id)
        
        if not admin_info:
            flash('Admin not found.', 'error')
            return redirect(url_for('admin.administrators'))
        
        return render_template('admin/edit.html', admin_info=admin_info)
        
    except Exception as e:
        print(f"Error editing admin: {e}")
        import traceback
        traceback.print_exc()
        flash('Error updating admin profile.', 'error')
        return redirect(url_for('admin.manage_admins'))
    finally:
        db.close()

@admin_bp.route('/admin/delete-admin/<string:admin_id>', methods=['POST'])
@super_admin_required
def delete_admin(admin_id):
    """Delete admin account (super admin only)"""
    db = SessionLocal()
    try:
        current_admin_id = session['admin_info']['id']
        result = admin_service.delete_admin(db, admin_id, current_admin_id)
        return jsonify(result)
    except Exception as e:
        print(f"Error deleting admin: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error deleting admin: {str(e)}'
        })
    finally:
        db.close()

@admin_bp.route('/admin/api/stats')
@super_admin_required
def admin_stats():
    """API endpoint for admin statistics"""
    db = SessionLocal()
    try:
        result = admin_service.get_admin_statistics(db)
        return jsonify(result)
    except Exception as e:
        print(f"Error fetching admin stats: {e}")
        return jsonify({"success": False, "message": "Error fetching statistics"})
    finally:
        db.close()

@admin_bp.route('/admin/demote-admin/<string:admin_id>', methods=['POST'])
@super_admin_required
def demote_admin_route(admin_id):
    """Demote admin to regular user (super admin only)"""
    db = SessionLocal()
    try:
        # Get admin info first
        admin = db.query(Admin).filter(Admin.id == admin_id).first()
        
        if not admin:
            return jsonify({'success': False, 'message': 'Admin not found'})
        
        # Prevent demoting yourself
        current_admin_id = session['admin_info']['id']
        if admin.id == current_admin_id:
            return jsonify({'success': False, 'message': 'You cannot demote yourself'})
        
        # Prevent demoting super admins
        if admin.role == AdminRole.super_admin:
            return jsonify({'success': False, 'message': 'Cannot demote super administrators'})
        
        # Store telegram_id and name before demotion
        telegram_id = admin.telegram_id
        admin_name = admin.full_name
        
        # ✅ Use UserService to demote admin to user
        result = user_service.demote_admin_to_user(db, telegram_id)
        
        if not result['success']:
            return jsonify(result)
        
        user = result['user']
        
        return jsonify({
            'success': True,
            'message': f'{admin_name} has been demoted to regular user successfully',
            'user': {
                'id': user.id,
                'full_name': user.full_name,
                'telegram_id': user.telegram_id
            }
        })
        
    except Exception as e:
        print(f"Error demoting admin: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error demoting admin: {str(e)}'})
    finally:
        db.close()

@admin_bp.route('/api/admins')
@super_admin_required
def get_admins_paginated():
    """Get all admins with formatted timestamps and pagination"""
    db = SessionLocal()
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        admins = admin_service.get_all_admins(db)
        
        # Apply pagination
        paginated_admins = Helpers.paginate(admins, page, per_page)
        
        formatted_admins = []
        for admin in paginated_admins:
            formatted_admins.append({
                'id': admin.id,
                'telegram_id': admin.telegram_id,
                'full_name': admin.full_name,
                'role': admin.role.value,
                'division': admin.division,
                'is_active': admin.is_active,
                'is_available': admin.is_available,
                'created_at': Helpers.format_timestamp(admin.created_at),
                'last_login': Helpers.format_timestamp(admin.last_login) if admin.last_login else 'Never'
            })
        
        return jsonify({
            'success': True,
            'admins': formatted_admins,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': len(admins),
                'total_pages': (len(admins) + per_page - 1) // per_page
            }
        })
    finally:
        db.close()

@admin_bp.route('/api/admin-logs')
@super_admin_required
def get_admin_logs():
    """Get admin activity audit logs with pagination"""
    db = SessionLocal()
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        logs = admin_service.get_audit_logs(db)
        
        # Apply pagination
        paginated_logs = Helpers.paginate(logs, page, per_page)
        
        formatted_logs = []
        for log in paginated_logs:
            formatted_logs.append({
                'id': log.id,
                'admin_id': log.admin_id,
                'admin_username': log.admin.username if log.admin else 'Unknown',
                'action': log.action,
                'description': log.description,
                'ip_address': log.ip_address,
                'timestamp': Helpers.format_timestamp(log.created_at)
            })
        
        return jsonify({
            'success': True,
            'logs': formatted_logs,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': len(logs),
                'total_pages': (len(logs) + per_page - 1) // per_page
            }
        })
    finally:
        db.close()