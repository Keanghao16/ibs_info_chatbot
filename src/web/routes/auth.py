from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from ...utils.apiClient import api_client
import os

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login():
    """Show Telegram login page"""
    bot_username = os.getenv("BOT_USERNAME", "YourBotUsername")
    return render_template('auth/login.html', bot_username=bot_username)

@auth_bp.route('/telegram', methods=['GET', 'POST'])
def telegram_auth():
    """Handle Telegram authentication callback"""
    telegram_data = {}
    
    # Telegram Login Widget sends data via GET parameters
    if request.method == 'GET' and request.args:
        # Get all Telegram auth data from query parameters
        for key in ['id', 'first_name', 'last_name', 'username', 'photo_url', 'auth_date', 'hash']:
            value = request.args.get(key)
            if value:
                telegram_data[key] = value
    
    # Debug logging
    print(f"Telegram auth data received: {telegram_data}")
    print(f"Request method: {request.method}")
    print(f"Request args: {dict(request.args)}")
    
    if not telegram_data.get('id'):
        flash('Invalid authentication data received', 'error')
        return redirect(url_for('auth.login'))
    
    # 🔄 FIXED: Call correct API endpoint
    response = api_client.post('/api/v1/auth/telegram-callback', telegram_data)  #  Added /api prefix
    
    if response.get('success'):
        data = response.get('data', {})
        
        # Store tokens and admin info in session
        session['access_token'] = data.get('access_token')
        session['refresh_token'] = data.get('refresh_token')
        session['admin'] = data.get('admin', {})
        session['admin_id'] = data.get('admin', {}).get('id')
        session.permanent = True
        
        flash(' Login successful!', 'success')
        return redirect(url_for('dashboard.index'))
    else:
        flash(f"❌ Authentication failed: {response.get('message', 'Unknown error')}", 'error')
        return redirect(url_for('auth.login'))

@auth_bp.route('/api-login-bridge', methods=['POST'])
def api_login_bridge():
    """Convert JWT token to web session"""
    data = request.get_json()
    access_token = data.get('access_token')
    
    if not access_token:
        return jsonify({'success': False, 'message': 'No access token provided'}), 400
    
    # 🔄 Verify token by calling API
    # Temporarily set token in session
    session['access_token'] = access_token
    
    # Test token by getting current user
    response = api_client.get('/api/v1/auth/me')
    
    if response.get('success'):
        admin_data = response.get('data')
        
        # Store in session for web app
        session['admin_id'] = admin_data.get('id')
        session['admin'] = admin_data
        session['access_token'] = access_token
        session.permanent = True
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'redirect_url': url_for('dashboard.index')
        }), 200
    else:
        session.clear()
        return jsonify({
            'success': False, 
            'message': response.get('message', 'Invalid token')
        }), 401

@auth_bp.route('/logout')
def logout():
    """Logout - clear session and optionally call API"""
    access_token = session.get('access_token')
    
    # Optional: Call API to invalidate token
    if access_token:
        api_client.post('/api/v1/auth/logout')
    
    session.clear()
    flash(' You have been logged out successfully', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
def profile():
    """Show admin profile page"""
    from ..auth_decorators import any_admin_required
    
    @any_admin_required
    def _profile():
        admin = session.get('admin', {})
        return render_template('auth/profile.html', admin=admin)
    
    return _profile()

#  ADD THIS MISSING ROUTE
@auth_bp.route('/update-profile', methods=['POST'])
def update_profile():
    """Update admin profile - calls API"""
    from ..auth_decorators import any_admin_required
    
    @any_admin_required
    def _update_profile():
        # Get form data
        full_name = request.form.get('full_name', '').strip()
        division = request.form.get('division', '').strip()
        
        # Validate
        if not full_name:
            flash('❌ Full name is required', 'error')
            return redirect(url_for('auth.profile'))
        
        # Prepare update data
        update_data = {
            'full_name': full_name
        }
        
        # Only include division for regular admins
        admin = session.get('admin', {})
        if admin.get('role') == 'admin':
            update_data['division'] = division if division else None
        
        # 🔄 Call API to update profile
        response = api_client.put('/api/v1/auth/update-profile', update_data)
        
        if response.get('success'):
            # Update session data with new info
            updated_admin = response.get('data')
            if updated_admin:
                session['admin'].update(updated_admin)
            
            flash(' Profile updated successfully!', 'success')
        else:
            if response.get('redirect_to_login'):
                flash('Session expired. Please login again.', 'error')
                return redirect(url_for('auth.login'))
            
            flash(f"❌ Error updating profile: {response.get('message', 'Unknown error')}", 'error')
        
        return redirect(url_for('auth.profile'))
    
    return _update_profile()

#  ADD THIS MISSING ROUTE
@auth_bp.route('/change-availability', methods=['POST'])
def change_availability():
    """Toggle availability - calls API"""
    from ..auth_decorators import any_admin_required
    
    @any_admin_required
    def _change_availability():
        # 🔄 Call API to toggle availability
        response = api_client.post('/api/v1/auth/toggle-availability')
        
        if response.get('success'):
            # Update session data
            data = response.get('data', {})
            if 'admin' in session and 'is_available' in data:
                session['admin']['is_available'] = data['is_available']
            
            flash(' Availability updated successfully!', 'success')
        else:
            if response.get('redirect_to_login'):
                flash('Session expired. Please login again.', 'error')
                return redirect(url_for('auth.login'))
            
            flash(f"❌ Error updating availability: {response.get('message', 'Unknown error')}", 'error')
        
        return redirect(url_for('auth.profile'))
    
    return _change_availability()