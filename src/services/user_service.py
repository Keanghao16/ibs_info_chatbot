from sqlalchemy.orm import Session
from ..database.models import User
from datetime import datetime, timedelta
from sqlalchemy import func, cast, Date

class UserService:
    """Service for user-related business logic"""
    
    @staticmethod
    def get_all_users(db: Session, page: int = 1, per_page: int = 10, search: str = None, is_premium: bool = None):
        """Get paginated users with optional filters"""
        query = db.query(User)
        
        # Apply filters
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (User.username.ilike(search_term)) |
                (User.first_name.ilike(search_term)) |
                (User.last_name.ilike(search_term))
            )
        
        if is_premium is not None:
            query = query.filter(User.is_premium == is_premium)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        users = query.order_by(User.registration_date.desc()).offset((page - 1) * per_page).limit(per_page).all()
        
        return {
            'users': users,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: str):  # ✅ Changed to string
        """Get user by ID (UUID)"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_telegram_id(db: Session, telegram_id: int):
        """Get user by Telegram ID"""
        return db.query(User).filter(User.telegram_id == telegram_id).first()
    
    @staticmethod
    def create_user(db: Session, user_data: dict):
        """Create new user"""
        user = User(**user_data)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def update_user(db: Session, user_id: str, update_data: dict):  # ✅ Changed to string
        """Update user"""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            for key, value in update_data.items():
                setattr(user, key, value)
            db.commit()
            db.refresh(user)
        return user
    
    @staticmethod
    def delete_user(db: Session, user_id: str):  # ✅ Changed to string
        """Delete user"""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            db.delete(user)
            db.commit()
        return True
    
    @staticmethod
    def get_user_statistics(db: Session):
        """Get user statistics"""
        total_users = db.query(User).count()
        premium_users = db.query(User).filter(User.is_premium == True).count()
        bot_users = db.query(User).filter(User.is_bot == True).count()
        
        now = datetime.utcnow()
        today_start = datetime(now.year, now.month, now.day)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        active_today = db.query(User).filter(
            cast(User.registration_date, Date) == today_start.date()
        ).count()
        
        active_week = db.query(User).filter(
            User.registration_date >= week_ago
        ).count()
        
        active_month = db.query(User).filter(
            User.registration_date >= month_ago
        ).count()
        
        new_today = db.query(User).filter(
            cast(User.registration_date, Date) == today_start.date()
        ).count()
        
        new_week = db.query(User).filter(
            User.registration_date >= week_ago
        ).count()
        
        new_month = db.query(User).filter(
            User.registration_date >= month_ago
        ).count()
        
        return {
            'total_users': total_users,
            'active_today': active_today,
            'active_this_week': active_week,
            'active_this_month': active_month,
            'premium_users': premium_users,
            'bot_users': bot_users,
            'new_users_today': new_today,
            'new_users_this_week': new_week,
            'new_users_this_month': new_month
        }
