from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from ..auth_decorators import any_admin_required, super_admin_required
from ...utils.apiClient import api_client

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@dashboard_bp.route('/')
@any_admin_required
def index():
    """Dashboard overview - now calls API"""
    
    # 🔄 Call API for dashboard stats
    stats_response = api_client.get('/api/v1/dashboard/stats')
    trends_response = api_client.get('/api/v1/dashboard/chat-trends', {
        'period': 'week',
        'limit': 7
    })
    
    # Handle API responses
    if not stats_response.get('success') or not trends_response.get('success'):
        if stats_response.get('redirect_to_login') or trends_response.get('redirect_to_login'):
            flash('Session expired. Please login again.', 'error')
            return redirect(url_for('auth.login'))
        
        flash('Error loading dashboard data', 'error')
        stats = {}
        trends = []
    else:
        stats = stats_response.get('data', {})
        trends = trends_response.get('data', [])
    
    # Get current admin info from session (set during login)
    current_admin = session.get('admin', {})
    
    return render_template('dashboard/index.html', 
                         stats=stats,
                         trends=trends,
                         current_admin=current_admin)







