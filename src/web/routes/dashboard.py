from flask import Blueprint, render_template, session, jsonify
from ...database.connection import SessionLocal
from ...database.models import Admin
from ...services.dashboard_service import DashboardService
from .auth import any_admin_required

dashboard_bp = Blueprint('dashboard', __name__)
dashboard_service = DashboardService()

@dashboard_bp.route('/dashboard')
@any_admin_required
def dashboard():
    """Main dashboard view"""
    db = SessionLocal()
    try:
        current_admin_id = session['admin_info']['id']
        admin_role = session['admin_info']['role']
        
        # Get dashboard data
        dashboard_data = dashboard_service.get_dashboard_data(db, current_admin_id, admin_role)
        
        return render_template('dashboard/index.html', **dashboard_data)
    finally:
        db.close()

@dashboard_bp.route('/dashboard/stats')
@any_admin_required
def dashboard_stats():
    """API endpoint for dashboard statistics"""
    db = SessionLocal()
    try:
        admin_id = session['admin_info']['id'] if session['admin_info']['role'] == 'admin' else None
        admin_role = session['admin_info']['role']
        
        result = dashboard_service.get_dashboard_stats(db, admin_id, admin_role)
        return jsonify(result)
    finally:
        db.close()

@dashboard_bp.route('/dashboard/activity')
@any_admin_required
def recent_activity():
    """API endpoint for recent activity"""
    db = SessionLocal()
    try:
        current_admin_id = session['admin_info']['id']
        activities = dashboard_service.get_recent_activity(db, current_admin_id)
        
        return jsonify({
            'success': True,
            'activities': [{
                'id': activity.id,
                'user_id': activity.user_id,
                'start_time': activity.start_time.isoformat() if activity.start_time else None,
                'status': activity.status
            } for activity in activities]
        })
    finally:
        db.close()







