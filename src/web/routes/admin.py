from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from ...database.connection import SessionLocal
from ...database.models import User, ChatSession, Admin, ChatMessage, AdminRole
from ...services.auth_service import AuthService
from ...services.admin_service import AdminService
from .auth import login_required, super_admin_required, any_admin_required

admin_bp = Blueprint('admin', __name__)
admin_service = AdminService()

@admin_bp.route('/manage-admins')
@super_admin_required
def manage_admins():
    db = SessionLocal()
    try:
        admins = admin_service.get_all_admins(db)
        return render_template('admin/manage_admins.html', admins=admins)
    finally:
        db.close()

@admin_bp.route('/admin/create-admin-telegram', methods=['POST'])
@super_admin_required
def create_admin_telegram():
    """Create new admin using Telegram ID"""
    db = SessionLocal()
    try:
        auth_service = AuthService()
        
        telegram_id = request.form.get('telegram_id')
        full_name = request.form.get('full_name')
        role = request.form.get('role', 'admin')
        division = request.form.get('division')
        
        result = auth_service.create_admin_telegram(
            db=db,
            telegram_id=telegram_id,
            full_name=full_name,
            role=role
        )
        
        if result['success']:
            if role == 'admin' and division:
                new_admin = db.query(Admin).filter(Admin.telegram_id == telegram_id).first()
                new_admin.division = division
                db.commit()
            
            flash('Admin created successfully!', 'success')
        else:
            flash(result['message'], 'error')
            
    except Exception as e:
        print(f"Error creating admin: {e}")
        flash('Error creating admin account.', 'error')
    finally:
        db.close()
    
    return redirect(url_for('admin.manage_admins'))

@admin_bp.route('/admin/toggle-admin-status/<int:admin_id>', methods=['POST'])
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
        
        return jsonify(result)
    finally:
        db.close()

@admin_bp.route('/admin-profile/<int:admin_id>')
@super_admin_required
def view_admin_profile(admin_id):
    """View another admin's profile"""
    db = SessionLocal()
    try:
        # Get the admin to view
        admin = db.query(Admin).filter(Admin.id == admin_id).first()
        
        if not admin:
            flash('Admin not found.', 'error')
            return redirect(url_for('admin.manage_admins'))
        
        # Create a temporary admin_info dict for the template
        admin_info = {
            'id': admin.id,
            'telegram_id': admin.telegram_id,
            'telegram_username': admin.telegram_username,
            'telegram_first_name': admin.telegram_first_name,
            'telegram_last_name': admin.telegram_last_name,
            'telegram_photo_url': admin.telegram_photo_url,
            'full_name': admin.full_name,
            'role': admin.role.value if admin.role else 'admin',
            'is_active': admin.is_active,
            'division': admin.division,
            'is_available': admin.is_available,
            'last_login': admin.last_login.strftime('%Y-%m-%d %H:%M:%S') if admin.last_login else None,
            'created_at': admin.created_at.strftime('%Y-%m-%d %H:%M:%S') if admin.created_at else None
        }
        
        # Flag to indicate this is viewing another admin's profile
        is_viewing_other = True
        
        return render_template('admin/admin_profile_view.html', 
                             admin_info=admin_info,
                             is_viewing_other=is_viewing_other)
    finally:
        db.close()