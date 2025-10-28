from sqlalchemy.orm import Session
from ..database.models import User
from datetime import datetime

class UserService:
    """Service for user-related business logic"""
    
    def get_all_users(self, db: Session):
        """Get all users"""
        return db.query(User).all()

    def get_user_by_id(self, db: Session, user_id: int):
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()

    def get_user_by_telegram_id(self, db: Session, telegram_id: str):
        """Get user by Telegram ID"""
        return db.query(User).filter(User.telegram_id == telegram_id).first()

    def find_or_create_user(self, db: Session, telegram_user):
        """Find existing user or create new one from Telegram user object"""
        existing_user = self.get_user_by_telegram_id(db, str(telegram_user.id))
        
        if existing_user:
            # Update user info if changed
            updated = False
            
            # Update individual fields
            if existing_user.first_name != telegram_user.first_name:
                existing_user.first_name = telegram_user.first_name
                updated = True
                
            if existing_user.last_name != telegram_user.last_name:
                existing_user.last_name = telegram_user.last_name
                updated = True
                
            if existing_user.username != telegram_user.username:
                existing_user.username = telegram_user.username
                updated = True
            
            # Update photo_url if available and different
            if hasattr(telegram_user, 'photo_url') and telegram_user.photo_url:
                if existing_user.photo_url != telegram_user.photo_url:
                    existing_user.photo_url = telegram_user.photo_url
                    updated = True
                    print(f"Updated user photo_url: {telegram_user.photo_url}")
                
            # Update full_name from first_name and last_name
            full_name = f"{telegram_user.first_name or ''} {telegram_user.last_name or ''}".strip()
            if existing_user.full_name != full_name:
                existing_user.full_name = full_name
                updated = True
                
            if not existing_user.is_active:
                existing_user.is_active = True
                updated = True
            
            # Update last activity
            existing_user.last_activity = datetime.now()
            updated = True
                
            if updated:
                db.commit()
                db.refresh(existing_user)
                print(f"User updated - photo_url in DB: {existing_user.photo_url}")
            
            return existing_user
        else:
            # Create new user
            photo_url = telegram_user.photo_url if hasattr(telegram_user, 'photo_url') else None
            
            user_data = {
                "telegram_id": str(telegram_user.id),
                "username": telegram_user.username,
                "first_name": telegram_user.first_name,
                "last_name": telegram_user.last_name,
                "photo_url": photo_url,
                "full_name": f"{telegram_user.first_name or ''} {telegram_user.last_name or ''}".strip(),
                "is_active": True,
                "last_activity": datetime.now()
            }
            
            print(f"Creating new user with photo_url: {photo_url}")
            return self.create_user(db, user_data)

    def create_user(self, db: Session, user_data: dict):
        """Create a new user"""
        new_user = User(**user_data)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print(f"User created - ID: {new_user.id}, photo_url: {new_user.photo_url}")
        return new_user

    def update_user(self, db: Session, user_id: int, user_data: dict):
        """Update existing user"""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            for key, value in user_data.items():
                setattr(user, key, value)
            db.commit()
            db.refresh(user)
        return user

    def delete_user(self, db: Session, user_id: int):
        """Delete user by ID"""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            db.delete(user)
            db.commit()
            return {"success": True, "message": "User deleted successfully"}
        return {"success": False, "message": "User not found"}

    def toggle_user_status(self, db: Session, user_id: int):
        """Toggle user active status"""
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return {"success": False, "message": "User not found"}
        
        user.is_active = not user.is_active
        db.commit()
        db.refresh(user)
        
        status = "activated" if user.is_active else "deactivated"
        return {
            "success": True,
            "message": f"User {status} successfully",
            "is_active": user.is_active
        }

    def deactivate_user(self, db: Session, telegram_id: str):
        """Deactivate user by Telegram ID"""
        user = self.get_user_by_telegram_id(db, telegram_id)
        if user:
            user.is_active = False
            db.commit()
            db.refresh(user)
        return user

    def update_user_photo(self, db: Session, telegram_id: str, photo_url: str):
        """Update user profile photo"""
        user = self.get_user_by_telegram_id(db, telegram_id)
        if user:
            user.photo_url = photo_url
            db.commit()
            db.refresh(user)
            print(f"Photo updated for user {telegram_id}: {photo_url}")
        return user