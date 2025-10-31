from sqlalchemy.orm import Session
from ..database.models import User, ChatSession, Admin, ChatMessage
from datetime import datetime
from ..utils import Helpers

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
    
    def get_recent_activities(self, db: Session, limit: int = 100):
        """Get recent system activities"""
        recent_users = db.query(User)\
            .order_by(User.created_at.desc())\
            .limit(limit)\
            .all()
        
        recent_chats = db.query(ChatMessage)\
            .order_by(ChatMessage.created_at.desc())\
            .limit(limit)\
            .all()
        
        activities = []
        
        for user in recent_users:
            activities.append({
                'type': 'user_registered',
                'description': f'New user registered: {user.full_name or user.username or "Unknown"}',
                'timestamp': Helpers.format_timestamp(user.created_at),
                'raw_timestamp': user.created_at
            })
        
        for chat in recent_chats:
            username = 'Unknown'
            if chat.user:
                username = chat.user.full_name or chat.user.username or 'Unknown'
            
            activities.append({
                'type': 'chat_message',
                'description': f'Chat from {username}',
                'timestamp': Helpers.format_timestamp(chat.created_at),
                'raw_timestamp': chat.created_at
            })
        
        # Sort by raw timestamp descending
        activities.sort(key=lambda x: x['raw_timestamp'], reverse=True)
        
        # Remove raw_timestamp from response
        for activity in activities:
            activity.pop('raw_timestamp', None)
        
        return activities[:limit]
    
    def get_statistics(self, db: Session):
        """Get dashboard statistics"""
        stats = {
            'total_users': db.query(User).count(),
            'total_chats': db.query(ChatMessage).count(),
            'total_admins': db.query(Admin).count(),
            'recent_activities': self.get_recent_activities(db, 5)
        }
        return stats