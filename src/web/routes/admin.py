from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from ...database.connection import SessionLocal
from ...services import AdminService, UserService  # ✅ Add UserService
from .auth import super_admin_required, any_admin_required
from ...database.models import Admin, AdminRole

admin_bp = Blueprint('admin', __name__)
admin_service = AdminService()
user_service = UserService()  # ✅ Create UserService instance

@admin_bp.route('/administrators')
@super_admin_required
def manage_admins():
    """List all administrators"""
    db = SessionLocal()
    try:
        admins = admin_service.get_all_admins(db)
        return render_template('admin/index.html', admins=admins)
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