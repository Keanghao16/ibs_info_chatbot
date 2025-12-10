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
        
        #  Ensure dates are datetime objects, not strings
        for user in users:
            # Convert string dates to datetime if needed
            if hasattr(user, 'registration_date') and isinstance(user.registration_date, str):
                try:
                    from datetime import datetime
                    user.registration_date = datetime.fromisoformat(user.registration_date.replace('Z', '+00:00'))
                except:
                    user.registration_date = None
            
            if hasattr(user, 'last_activity') and isinstance(user.last_activity, str):
                try:
                    from datetime import datetime
                    user.last_activity = datetime.fromisoformat(user.last_activity.replace('Z', '+00:00'))
                except:
                    user.last_activity = None
        
        return {
            'users': users,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: str):  #  Changed to string
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
    def update_user(db: Session, user_id: str, update_data: dict):  #  Changed to string
        """Update user"""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            for key, value in update_data.items():
                setattr(user, key, value)
            db.commit()
            db.refresh(user)
        return user
    
    @staticmethod
    def delete_user(db: Session, user_id: str):  #  Changed to string
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
    
    @staticmethod
    def get_user_or_admin_by_telegram_id(db: Session, telegram_id: str):
        """Check if telegram_id belongs to admin or user"""
        from ..database.models import Admin
        
        # Check if admin first
        admin = db.query(Admin).filter(Admin.telegram_id == telegram_id).first()
        if admin:
            return {
                'type': 'admin',
                'data': admin
            }
        
        # Check if user
        user = db.query(User).filter(User.telegram_id == int(telegram_id)).first()
        if user:
            return {
                'type': 'user',
                'data': user
            }
        
        return None

    @staticmethod
    def create_user_if_not_admin(db: Session, telegram_id: str, username: str = None, 
                                  first_name: str = None, last_name: str = None, 
                                  full_name: str = None, photo_url: str = None):
        """Create user only if they're not an admin"""
        from ..database.models import Admin
        
        # Check if admin
        admin = db.query(Admin).filter(Admin.telegram_id == telegram_id).first()
        if admin:
            return {
                'success': False,
                'message': 'Cannot create user - this telegram_id belongs to an admin',
                'user': None
            }
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.telegram_id == int(telegram_id)).first()
        if existing_user:
            # Update last activity and photo if provided
            existing_user.last_activity = datetime.now()
            if photo_url:
                existing_user.photo_url = photo_url
            db.commit()
            db.refresh(existing_user)
            return {
                'success': True,
                'message': 'User already exists',
                'user': existing_user
            }
        
        # Create new user
        new_user = User(
            telegram_id=int(telegram_id),
            username=username,
            first_name=first_name,
            last_name=last_name,
            photo_url=photo_url,  # ✅ ADD THIS LINE
            registration_date=datetime.now(),
            last_activity=datetime.now()
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {
            'success': True,
            'message': 'User created successfully',
            'user': new_user
        }
