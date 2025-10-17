from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from ...database.connection import SessionLocal
from ...services.auth_service import AuthService
from ...database.models import AdminRole, Admin
from functools import wraps
import os
import hashlib
import hmac
import time

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService()

def login_required(f):
    """Decorator to require login for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_token' not in session:
            return redirect(url_for('auth.login'))
        
        # Verify token
        token_result = auth_service.verify_token(session['admin_token'])
        if not token_result['success']:
            session.pop('admin_token', None)
            flash('Session expired. Please login again.', 'error')
            return redirect(url_for('auth.login'))
        
        return f(*args, **kwargs)
    return decorated_function

def super_admin_required(f):
    """Decorator to require super_admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_info' not in session:
            flash('Access denied. Please login.', 'error')
            return redirect(url_for('auth.login'))
        
        admin_role = session['admin_info'].get('role')
        if admin_role != 'super_admin':
            flash('Access denied. Super Admin privileges required.', 'error')
            return redirect(url_for('admin.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

def any_admin_required(f):
    """Decorator for routes accessible by both super_admin and admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_info' not in session:
            flash('Access denied. Please login.', 'error')
            return redirect(url_for('auth.login'))
        
        admin_role = session['admin_info'].get('role')
        if admin_role not in ['super_admin', 'admin']:
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('auth.login'))
        
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login')
def login():
    """Show Telegram login page"""
    bot_username = os.getenv("BOT_USERNAME", "YourBotUsername")  # Add this to .env
    return render_template('auth/login.html', bot_username=bot_username)

@auth_bp.route('/auth/telegram', methods=['GET', 'POST'])
def telegram_auth():
    """Handle Telegram authentication callback"""
    telegram_data = {}
    
    # Telegram Login Widget sends data via GET parameters, not POST
    if request.method == 'GET':
        # Get all Telegram auth data from query parameters
        for key in ['id', 'first_name', 'last_name', 'username', 'photo_url', 'auth_date', 'hash']:
            value = request.args.get(key)
            if value:
                telegram_data[key] = value
    else:  # POST fallback
        # Get all Telegram auth data from form
        for key in ['id', 'first_name', 'last_name', 'username', 'photo_url', 'auth_date', 'hash']:
            value = request.form.get(key)
            if value:
                telegram_data[key] = value
    
    # Debug logging
    print(f"Telegram auth data received: {telegram_data}")
    
    if not telegram_data.get('id'):
        flash('Invalid authentication data', 'error')
        return redirect(url_for('auth.login'))
    
    db = SessionLocal()
    try:
        result = auth_service.authenticate_admin_telegram(db, telegram_data)
        
        if result['success']:
            session['admin_token'] = result['token']
            session['admin_info'] = result['admin']
            flash('Login successful!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash(result['message'], 'error')
            return redirect(url_for('auth.login'))
    except Exception as e:
        print(f"Auth error: {e}")
        flash('Authentication error occurred', 'error')
        return redirect(url_for('auth.login'))
    finally:
        db.close()

@auth_bp.route('/logout')
def logout():
    session.pop('admin_token', None)
    session.pop('admin_info', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html')

@auth_bp.route('/auth/update-profile', methods=['POST'])
@login_required
def update_profile():
    """Update admin profile information."""
    full_name = request.form.get('full_name', '').strip()
    division = request.form.get('division', '').strip()
    
    if not full_name:
        flash('Full name is required.', 'error')
        return redirect(url_for('auth.profile'))
    
    db = SessionLocal()
    try:
        admin_id = session.get('admin_info', {}).get('id')
        admin = db.query(Admin).filter(Admin.id == admin_id).first()
        
        if admin:
            admin.full_name = full_name
            if admin.role == AdminRole.admin:  # Only regular admins have divisions
                admin.division = division
            db.commit()
            
            # Update session info
            session['admin_info']['full_name'] = full_name
            if admin.role == AdminRole.admin:
                session['admin_info']['division'] = division
            
            flash('Profile updated successfully!', 'success')
        else:
            flash('Admin not found.', 'error')
    except Exception as e:
        print(f"Error updating profile: {e}")
        flash('Error updating profile.', 'error')
    finally:
        db.close()
    
    return redirect(url_for('auth.profile'))

@auth_bp.route('/auth/change-availability', methods=['POST'])
@any_admin_required
def change_availability():
    """Toggle admin availability for chat assignment."""
    if session.get('admin_info', {}).get('role') != 'admin':
        flash('Only regular admins can change availability status.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    db = SessionLocal()
    try:
        admin_id = session.get('admin_info', {}).get('id')
        admin = db.query(Admin).filter(Admin.id == admin_id).first()
        
        if admin:
            admin.is_available = not admin.is_available
            db.commit()
            
            # Update session info
            session['admin_info']['is_available'] = admin.is_available
            
            status = "available" if admin.is_available else "unavailable"
            flash(f"You are now {status} for new chat assignments.", "success")
        else:
            flash("Admin not found.", "error")
    except Exception as e:
        print(f"Error changing availability: {e}")
        flash("Error updating availability status.", "error")
    finally:
        db.close()
    
    return redirect(url_for('admin.dashboard'))