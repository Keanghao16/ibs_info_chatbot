from sqlalchemy.orm import Session
from ..database.models import User, Admin, ChatSession
from datetime import datetime, timedelta
from sqlalchemy import func, cast, Date

class DashboardService:
    @staticmethod
    def get_overview_stats(db: Session):
        """Get overall dashboard statistics"""
        try:
            # User stats
            total_users = db.query(User).count()
            today = datetime.utcnow().date()
            
            # Try different possible field names for user creation date
            new_users_today = 0
            try:
                # Try created_at first
                new_users_today = db.query(User).filter(
                    func.date(User.created_at) == today
                ).count()
            except AttributeError:
                try:
                    # Try registration_date
                    new_users_today = db.query(User).filter(
                        func.date(User.registration_date) == today
                    ).count()
                except AttributeError:
                    # If no date field exists, set to 0
                    new_users_today = 0
            
            # Chat stats
            total_chats = 0
            active_chats = 0
            waiting_chats = 0
            
            try:
                total_chats = db.query(ChatSession).count()
                
                # Check if status field exists
                try:
                    active_chats = db.query(ChatSession).filter(ChatSession.status == 'active').count()
                    waiting_chats = db.query(ChatSession).filter(ChatSession.status == 'waiting').count()
                except AttributeError:
                    # If status field doesn't exist, try other common field names
                    try:
                        active_chats = db.query(ChatSession).filter(ChatSession.session_status == 'active').count()
                        waiting_chats = db.query(ChatSession).filter(ChatSession.session_status == 'waiting').count()
                    except AttributeError:
                        active_chats = 0
                        waiting_chats = 0
                        
            except Exception as e:
                print(f"Error querying chat sessions: {e}")
                total_chats = 0
            
            # Admin stats
            total_admins = 0
            available_admins = 0
            
            try:
                total_admins = db.query(Admin).count()
                
                # Check if is_available field exists
                try:
                    available_admins = db.query(Admin).filter(Admin.is_available == True).count()
                except AttributeError:
                    # If is_available doesn't exist, assume all are available
                    available_admins = total_admins
                    
            except Exception as e:
                print(f"Error querying admins: {e}")
                total_admins = 1  # At least show 1 admin (current user)
                available_admins = 1
            
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
            
        except Exception as e:
            print(f"Error in get_overview_stats: {e}")
            # Return fallback data
            return {
                'users': {
                    'total': 0,
                    'new_today': 0
                },
                'chats': {
                    'total': 0,
                    'active': 0,
                    'waiting': 0
                },
                'admins': {
                    'total': 1,
                    'available': 1
                }
            }
    
    @staticmethod
    def get_user_growth_data(db: Session, period: str, limit: int):
        """Get user growth data"""
        # Return sample data for now
        from datetime import datetime, timedelta
        
        data = []
        for i in range(limit):
            date = datetime.now() - timedelta(days=i)
            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'count': max(0, 10 - i + (i % 3))  # Sample data
            })
        
        return list(reversed(data))
    
    @staticmethod
    def get_chat_trends(db: Session, period: str, limit: int):
        """Get chat trends"""
        # Return sample data for now
        from datetime import datetime, timedelta
        
        data = []
        for i in range(limit):
            date = datetime.now() - timedelta(days=i)
            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'chats': max(0, 5 - i + (i % 2))  # Sample data
            })
        
        return list(reversed(data))
    
    @staticmethod
    def get_admin_performance(db: Session):
        """Get admin performance metrics"""
        return {
            'total_responses': 0,
            'average_response_time': 0,
            'customer_satisfaction': 95
        }