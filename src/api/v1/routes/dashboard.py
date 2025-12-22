"""
Dashboard API Routes
Handles dashboard statistics and analytics endpoints
"""

from flask import Blueprint, request, jsonify
from ..middleware.auth import token_required, admin_required
from ..schemas import success_response, error_response
from ....services.dashboard_service import DashboardService
from ....database.connection import get_db_session

# Create blueprint
dashboard_api_bp = Blueprint('dashboard_api', __name__)


@dashboard_api_bp.route('/dashboard/stats', methods=['GET'])
@token_required
@admin_required
def get_dashboard_stats(current_user):
    """
    Get overall dashboard statistics
    
    Returns:
        - User stats (total, active, new)
        - Chat stats (total, active, waiting)
        - Admin stats (total, available)
        - Recent activity
    """
    db = get_db_session()
    try:
        stats = DashboardService.get_overview_stats(db)
        
        return success_response(
            data=stats,
            message="Dashboard statistics retrieved successfully"
        )
        
    except Exception as e:
        return error_response(str(e), 500)
    finally:
        db.close()


@dashboard_api_bp.route('/dashboard/user-growth', methods=['GET'])
@token_required
@admin_required
def get_user_growth(current_user):
    """
    Get user growth data
    
    Query Parameters:
        - period (str): day/week/month (default: month)
        - limit (int): Number of data points (default: 30)
    """
    db = get_db_session()
    try:
        period = request.args.get('period', 'month')
        limit = request.args.get('limit', 30, type=int)
        
        growth_data = DashboardService.get_user_growth_data(db, period, limit)
        
        return success_response(
            data=growth_data,
            message="User growth data retrieved successfully"
        )
        
    except Exception as e:
        return error_response(str(e), 500)
    finally:
        db.close()


@dashboard_api_bp.route('/dashboard/chat-trends', methods=['GET'])
@token_required
@admin_required
def get_chat_trends(current_user):
    """
    Get chat trends and patterns
    
    Query Parameters:
        - period (str): day/week/month
        - limit (int): Number of data points
    """
    db = get_db_session()
    try:
        period = request.args.get('period', 'week')
        limit = request.args.get('limit', 7, type=int)
        
        trends = DashboardService.get_chat_trends(db, period, limit)
        
        return success_response(
            data=trends,
            message="Chat trends retrieved successfully"
        )
        
    except Exception as e:
        return error_response(str(e), 500)
    finally:
        db.close()


@dashboard_api_bp.route('/dashboard/admin-performance', methods=['GET'])
@token_required
@admin_required
def get_admin_performance(current_user):
    """
    Get admin performance metrics
    
    Returns:
        - Chats handled per admin
        - Average response time
        - Customer satisfaction (if available)
    """
    db = get_db_session()
    try:
        performance = DashboardService.get_admin_performance(db)
        
        return success_response(
            data=performance,
            message="Admin performance data retrieved successfully"
        )
        
    except Exception as e:
        return error_response(str(e), 500)
    finally:
        db.close()