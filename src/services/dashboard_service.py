from sqlalchemy.orm import Session
from ..database.models import User, Admin, ChatSession
from datetime import datetime, timedelta

class DashboardService:
    @staticmethod
    def get_overview_stats(db: Session):
        """Get overall dashboard statistics"""
        # User stats
        total_users = db.query(User).count()
        today = datetime.utcnow().date()
        new_users_today = db.query(User).filter(User.created_at >= today).count()
        
        # Chat stats
        total_chats = db.query(ChatSession).count()
        active_chats = db.query(ChatSession).filter(ChatSession.status == 'active').count()
        waiting_chats = db.query(ChatSession).filter(ChatSession.status == 'waiting').count()
        
        # Admin stats
        total_admins = db.query(Admin).count()
        available_admins = db.query(Admin).filter(Admin.is_available == True).count()
        
        return {
            'users': {
                'total': total_users,
                'new_today': new_users_today
            },
            'chats': {
                'total': total_chats,
                'active': active_chats,
                'waiting': waiting_chats
            },
            'admins': {
                'total': total_admins,
                'available': available_admins
            }
        }
    
    @staticmethod
    def get_user_growth_data(db: Session, period: str, limit: int):
        """Get user growth data"""
        # TODO: Implement based on period
        return []
    
    @staticmethod
    def get_chat_trends(db: Session, period: str, limit: int):
        """Get chat trends"""
        # TODO: Implement based on period
        return []
    
    @staticmethod
    def get_admin_performance(db: Session):
        """Get admin performance metrics"""
        # TODO: Implement
        return []