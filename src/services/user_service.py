from sqlalchemy.orm import Session
from ..database.models import User, Admin
from datetime import datetime
import uuid

class UserService:
    """Service for user-related business logic"""
    
    def get_user_by_id(self, db: Session, user_id: str):
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_telegram_id(self, db: Session, telegram_id: str):
        """Get user by Telegram ID"""
        return db.query(User).filter(User.telegram_id == telegram_id).first()
    
    def get_all_users(self, db: Session):
        """Get all users"""
        return db.query(User).order_by(User.created_at.desc()).all()
    
    def get_user_or_admin_by_telegram_id(self, db: Session, telegram_id: str):
        """Check if telegram_id exists in User or Admin table"""
        user = self.get_user_by_telegram_id(db, telegram_id)
        if user:
            return {'type': 'user', 'data': user}
        
        admin = db.query(Admin).filter(Admin.telegram_id == telegram_id).first()
        if admin:
            return {'type': 'admin', 'data': admin}
        
        return None
    
    def create_user_if_not_admin(self, db: Session, telegram_id: str, **user_data):
        """Create a new user if the telegram_id doesn't belong to an admin"""
        # Check if already exists as admin
        admin = db.query(Admin).filter(Admin.telegram_id == telegram_id).first()
        if admin:
            return {'success': False, 'message': 'This Telegram ID belongs to an admin'}
        
        # Check if user already exists
        existing_user = self.get_user_by_telegram_id(db, telegram_id)
        if existing_user:
            return {'success': False, 'message': 'User already exists'}
        
        # Create new user
        new_user = User(
            id=str(uuid.uuid4()),
            telegram_id=telegram_id,
            username=user_data.get('username'),
            first_name=user_data.get('first_name'),
            last_name=user_data.get('last_name'),
            full_name=user_data.get('full_name', ''),
            photo_url=user_data.get('photo_url'),
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {'success': True, 'user': new_user}
    
    def promote_user_to_admin(self, db: Session, telegram_id: str, promoted_by_admin_id: str, **admin_data):
        """Promote a user to admin"""
        # Check if user exists
        user = self.get_user_by_telegram_id(db, telegram_id)
        if not user:
            return {'success': False, 'message': 'User not found'}
        
        # Check if already an admin
        admin = db.query(Admin).filter(Admin.telegram_id == telegram_id).first()
        if admin:
            return {'success': False, 'message': 'User is already an admin'}
        
        # Store user data before deletion
        user_data_copy = {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': user.full_name or admin_data.get('full_name', ''),
            'photo_url': user.photo_url
        }
        
        # ✅ Delete user record FIRST
        db.delete(user)
        db.flush()  # Flush to database but don't commit yet
        
        # ✅ Then create admin record
        new_admin = Admin(
            id=str(uuid.uuid4()),
            telegram_id=telegram_id,
            full_name=admin_data.get('full_name', user_data_copy['full_name']),
            telegram_username=user_data_copy['username'],
            telegram_first_name=user_data_copy['first_name'],
            telegram_last_name=user_data_copy['last_name'],
            telegram_photo_url=user_data_copy['photo_url'],
            role=admin_data.get('role', 'admin'),
            is_active=True,
            is_available=admin_data.get('is_available', True),
            division=admin_data.get('division'),
            created_at=datetime.utcnow()
        )
        
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)
        
        return {'success': True, 'admin': new_admin}
    
    def demote_admin_to_user(self, db: Session, telegram_id: str):
        """Demote an admin to user"""
        # Check if admin exists
        admin = db.query(Admin).filter(Admin.telegram_id == telegram_id).first()
        if not admin:
            return {'success': False, 'message': 'Admin not found'}
        
        # Check if user already exists
        user = self.get_user_by_telegram_id(db, telegram_id)
        if user:
            return {'success': False, 'message': 'User already exists'}
        
        # ✅ Store admin data before deletion
        admin_data = {
            'telegram_id': admin.telegram_id,
            'username': admin.telegram_username,
            'first_name': admin.telegram_first_name,
            'last_name': admin.telegram_last_name,
            'full_name': admin.full_name,
            'photo_url': admin.telegram_photo_url
        }
        
        # ✅ Delete admin record FIRST
        db.delete(admin)
        db.flush()  # Flush to database but don't commit yet
        
        # ✅ Then create user record
        new_user = User(
            id=str(uuid.uuid4()),
            telegram_id=admin_data['telegram_id'],
            username=admin_data['username'],
            first_name=admin_data['first_name'],
            last_name=admin_data['last_name'],
            full_name=admin_data['full_name'],
            photo_url=admin_data['photo_url'],
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {'success': True, 'user': new_user}
    
    def delete_user(self, db: Session, user_id: str):
        """Delete a user"""
        user = self.get_user_by_id(db, user_id)
        if not user:
            return {'success': False, 'message': 'User not found'}
        
        db.delete(user)
        db.commit()
        
        return {'success': True, 'message': f'User {user.full_name} deleted successfully'}
    
    def toggle_user_status(self, db: Session, user_id: str):
        """Toggle user active status"""
        user = self.get_user_by_id(db, user_id)
        if not user:
            return {'success': False, 'message': 'User not found'}
        
        user.is_active = not user.is_active
        db.commit()
        
        status = 'activated' if user.is_active else 'deactivated'
        return {'success': True, 'message': f'User {status} successfully', 'is_active': user.is_active}


# Keep any existing standalone functions below if needed for backward compatibility
# Or remove them if you want to use only the class-based approach
