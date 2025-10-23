from sqlalchemy.orm import Session
from ..database.models import User, ChatSession, Admin
from datetime import datetime

class DashboardService:
    """Service for dashboard-related business logic"""
    
    def get_dashboard_data(self, db: Session, admin_id: int, admin_role: str):
        """Get all dashboard data for an admin"""
        data = {
            'users': db.query(User).all(),
            'chats': db.query(ChatSession).all(),
            'current_admin': db.query(Admin).filter(Admin.id == admin_id).first()
        }
        
        # If admin role, get their specific chats
        if admin_role == 'admin':
            data['admin_chats'] = db.query(ChatSession).filter(
                ChatSession.admin_id == admin_id
            ).all()
        
        return data
    
    def get_dashboard_stats(self, db: Session, admin_id: int = None, admin_role: str = None):
        """Get dashboard statistics"""
        stats = {
            "users_count": db.query(User).count(),
            "chats_count": db.query(ChatSession).count(),
            "active_chats_count": db.query(ChatSession).filter(
                ChatSession.status == 'active'
            ).count()
        }
        
        # If admin role, get their specific stats
        if admin_role == 'admin' and admin_id:
            stats["admin_chats_count"] = db.query(ChatSession).filter(
                ChatSession.admin_id == admin_id
            ).count()
            stats["admin_active_chats"] = db.query(ChatSession).filter(
                ChatSession.admin_id == admin_id,
                ChatSession.status == 'active'
            ).count()
        
        # If super admin, get admin count
        if admin_role == 'super_admin':
            stats["admins_count"] = db.query(Admin).count()
        
        return {"success": True, "stats": stats}
    
    def get_recent_activity(self, db: Session, admin_id: int, limit: int = 10):
        """Get recent activity for an admin"""
        # This can be expanded based on your needs
        # For now, return basic session info
        recent_sessions = db.query(ChatSession).filter(
            ChatSession.admin_id == admin_id
        ).order_by(ChatSession.start_time.desc()).limit(limit).all()
        
        return recent_sessions