from flask import Blueprint, render_template, session, jsonify, request
from ...database.connection import SessionLocal
from ...database.models import Admin
from ...services.dashboard_service import DashboardService
from .auth import any_admin_required
from ...utils import Helpers

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
        current_admin_id = session['admin_info']['id']
        admin_role = session['admin_info']['role']
        
        stats = dashboard_service.get_dashboard_stats(db, current_admin_id, admin_role)
        return jsonify(stats)
    finally:
        db.close()

@dashboard_bp.route('/dashboard/activity')
@any_admin_required
def recent_activity():
    """API endpoint for recent activity with pagination"""
    db = SessionLocal()
    try:
        current_admin_id = session['admin_info']['id']
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        activities = dashboard_service.get_recent_activities(db, limit=100)
        
        # Apply pagination
        paginated_activities = Helpers.paginate(activities, page, per_page)
        
        return jsonify({
            'success': True,
            'activities': paginated_activities,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': len(activities),
                'total_pages': (len(activities) + per_page - 1) // per_page
            }
        })
    finally:
        db.close()







