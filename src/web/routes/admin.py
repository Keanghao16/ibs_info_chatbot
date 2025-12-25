from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from ..auth_decorators import any_admin_required, super_admin_required
from ...utils.apiClient import api_client

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admins')
@any_admin_required
def list_admins():
    """List all admins - now calls API"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # 🔄 Call API for admins list
    response = api_client.get('/api/v1/admins', {
        'page': page,
        'per_page': per_page
    })
    
    # 🔄 Call API for admin statistics
    stats_response = api_client.get('/api/v1/admins/stats')
    
    # Handle admins list response
    if not response.get('success'):
        if response.get('redirect_to_login'):
            flash('Session expired. Please login again.', 'error')
            return redirect(url_for('auth.login'))
        
        flash(f"Error loading admins: {response.get('message', 'Unknown error')}", 'error')
        admins = []
        pagination_data = {}
    else:
        admins = response.get('data', [])
        pagination_data = response.get('pagination', {})
    
    # Handle stats response
    if not stats_response.get('success'):
        # Fallback stats if API fails - calculate from current page
        stats = {
            'total_admins': len(admins),
            'super_admins': len([a for a in admins if a.get('role') == 'super_admin']),
            'active_admins': len([a for a in admins if a.get('is_active')]),
            'available_admins': len([a for a in admins if a.get('is_available')]),
            'online_now': 0
        }
    else:
        stats = stats_response.get('data', {})
        # Calculate regular admins count if not provided
        if 'regular_admins' not in stats:
            total = stats.get('total_admins', 0)
            super_count = stats.get('super_admins', 0)
            stats['regular_admins'] = max(0, total - super_count)
    
    return render_template('admin/index.html', 
                         admins=admins,
                         stats=stats,  # Pass stats to template
                         # Individual pagination variables
                         page=pagination_data.get('page', 1),
                         per_page=pagination_data.get('per_page', 20),
                         total=pagination_data.get('total', 0),
                         total_pages=pagination_data.get('total_pages', 1),
                         has_next=pagination_data.get('has_next', False),
                         has_prev=pagination_data.get('has_prev', False),
                         pagination=pagination_data)

@admin_bp.route('/admins/<admin_id>')
@any_admin_required
def view_admin(admin_id):
    """View single admin - now calls API"""
    # 🔄 Call API instead of service
    response = api_client.get(f'/api/v1/admins/{admin_id}')
    
    if not response.get('success'):
        if response.get('redirect_to_login'):
            flash('Session expired. Please login again.', 'error')
            return redirect(url_for('auth.login'))
        
        flash(f"Error loading admin: {response.get('message', 'Admin not found')}", 'error')
        return redirect(url_for('admin.list_admins'))
    
    admin = response.get('data')
    return render_template('admin/view.html', admin=admin)

@admin_bp.route('/admin/create-admin-telegram', methods=['POST'])
@super_admin_required
def create_admin_telegram():
    """Create new admin using Telegram ID - now calls API"""
    telegram_id = request.form.get('telegram_id')
    full_name = request.form.get('full_name')
    role = request.form.get('role', 'admin')
    division = request.form.get('division')
    
    # Validate inputs
    if not telegram_id or not full_name:
        flash('❌ Telegram ID and full name are required', 'error')
        return redirect(url_for('admin.list_admins'))
    
    # 🔄 Call API instead of service
    admin_data = {
        'telegram_id': telegram_id,
        'full_name': full_name,
        'role': role,
        'division': division
    }
    
    response = api_client.post('/api/v1/admins', admin_data)
    
    if response.get('success'):
        flash(' Admin created successfully!', 'success')
    else:
        if response.get('redirect_to_login'):
            flash('Session expired. Please login again.', 'error')
            return redirect(url_for('auth.login'))
        
        flash(f"❌ Error creating admin: {response.get('message', 'Unknown error')}", 'error')
    
    return redirect(url_for('admin.list_admins'))

@admin_bp.route('/admin/toggle-admin-status/<string:admin_id>', methods=['POST'])
@super_admin_required
def toggle_admin_status(admin_id):
    """Toggle admin active status - now calls API"""
    # 🔄 Call API instead of service
    response = api_client.put(f'/api/v1/admins/{admin_id}/toggle-status')
    
    if response.get('success'):
        return jsonify(response)
    else:
        if response.get('redirect_to_login'):
            return jsonify({'success': False, 'message': 'Session expired'})
        
        return jsonify({
            'success': False, 
            'message': response.get('message', 'Error updating admin status')
        })

@admin_bp.route('/admin/toggle-availability', methods=['POST'])
@any_admin_required
def toggle_availability():
    """Toggle admin availability for taking new chats - now calls API"""
    # 🔄 Call API instead of service
    response = api_client.post('/api/v1/auth/toggle-availability')
    
    if response.get('success'):
        # Update session data
        if 'admin' in session and 'is_available' in response.get('data', {}):
            session['admin']['is_available'] = response['data']['is_available']
        return jsonify(response)
    else:
        if response.get('redirect_to_login'):
            return jsonify({'success': False, 'message': 'Session expired'})
        
        return jsonify({
            'success': False, 
            'message': response.get('message', 'Error updating availability')
        })

@admin_bp.route('/administrators/<string:admin_id>')
@super_admin_required
def view_admin_profile(admin_id):
    """View another admin's profile - now calls API"""
    # Same as view_admin but with different template context
    return view_admin(admin_id)

@admin_bp.route('/administrators/<string:admin_id>/edit', methods=['GET', 'POST'])
@super_admin_required
def edit_admin(admin_id):
    """Edit admin profile - now calls API"""
    if request.method == 'POST':
        # Get form data
        full_name = request.form.get('full_name', '').strip()
        division = request.form.get('division', '').strip()
        role = request.form.get('role')
        
        # Validate
        if not full_name:
            flash('❌ Full name is required', 'error')
            return redirect(request.url)
        
        # Update admin using API
        update_data = {
            'full_name': full_name,
            'role': role
        }
        
        # Only add division for regular admins
        if role == 'admin':
            update_data['division'] = division if division else None
        
        response = api_client.put(f'/api/v1/admins/{admin_id}', update_data)
        
        if response.get('success'):
            flash(' Admin profile updated successfully!', 'success')
            return redirect(url_for('admin.view_admin', admin_id=admin_id))
        else:
            if response.get('redirect_to_login'):
                flash('Session expired. Please login again.', 'error')
                return redirect(url_for('auth.login'))
            
            flash(f"❌ Error updating admin: {response.get('message', 'Unknown error')}", 'error')
    
    # GET request - show edit form
    response = api_client.get(f'/api/v1/admins/{admin_id}')
    
    if not response.get('success'):
        if response.get('redirect_to_login'):
            flash('Session expired. Please login again.', 'error')
            return redirect(url_for('auth.login'))
        
        flash('Admin not found.', 'error')
        return redirect(url_for('admin.list_admins'))
    
    admin_info = response.get('data')
    return render_template('admin/edit.html', admin_info=admin_info)

@admin_bp.route('/admin/delete-admin/<string:admin_id>', methods=['POST'])
@super_admin_required
def delete_admin(admin_id):
    """Delete admin account (super admin only) - now calls API"""
    current_admin_id = session['admin']['id']
    
    # Prevent self-deletion
    if admin_id == current_admin_id:
        return jsonify({
            'success': False,
            'message': 'You cannot delete your own account'
        })
    
    # 🔄 Call API instead of service
    response = api_client.delete(f'/api/v1/admins/{admin_id}')
    
    if response.get('success'):
        return jsonify(response)
    else:
        if response.get('redirect_to_login'):
            return jsonify({'success': False, 'message': 'Session expired'})
        
        return jsonify({
            'success': False,
            'message': response.get('message', 'Error deleting admin')
        })

@admin_bp.route('/admin/api/stats')
@super_admin_required
def admin_stats():
    """API endpoint for admin statistics - now calls API"""
    # 🔄 Call API instead of service
    response = api_client.get('/api/v1/admins/stats')
    
    if response.get('success'):
        return jsonify(response)
    else:
        if response.get('redirect_to_login'):
            return jsonify({'success': False, 'message': 'Session expired'})
        
        return jsonify({
            'success': False,
            'message': response.get('message', 'Error fetching statistics')
        })

@admin_bp.route('/admin/demote-admin/<string:admin_id>', methods=['POST'])
@super_admin_required
def demote_admin_route(admin_id):
    """Demote admin to regular user (super admin only) - now calls API"""
    current_admin_id = session['admin']['id']
    
    # Prevent self-demotion
    if admin_id == current_admin_id:
        return jsonify({
            'success': False,
            'message': 'You cannot demote your own account'
        })
    
    # 🔄 Call API for demotion (this endpoint needs to be implemented in API)
    response = api_client.post(f'/api/v1/admins/{admin_id}/demote')
    
    if response.get('success'):
        return jsonify(response)
    else:
        if response.get('redirect_to_login'):
            return jsonify({'success': False, 'message': 'Session expired'})
        
        return jsonify({
            'success': False,
            'message': response.get('message', 'Demotion feature not implemented yet')
        })