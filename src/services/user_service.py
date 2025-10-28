from sqlalchemy.orm import Session
from src.database.models import User, Admin, AdminRole
from datetime import datetime
from typing import Optional, Tuple
import uuid

def get_user_or_admin_by_telegram_id(db: Session, telegram_id: str) -> Tuple[Optional[object], Optional[str]]:
    """
    Check if telegram_id exists and return (record, type)
    Returns: (User/Admin object or None, 'user'/'admin'/None)
    """
    # Check admin first (higher priority)
    admin = db.query(Admin).filter(Admin.telegram_id == telegram_id).first()
    if admin:
        return admin, "admin"
    
    # Check user
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if user:
        return user, "user"
    
    return None, None

def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    """Get user by UUID"""
    return db.query(User).filter(User.id == user_id).first()

def get_admin_by_id(db: Session, admin_id: str) -> Optional[Admin]:
    """Get admin by UUID"""
    return db.query(Admin).filter(Admin.id == admin_id).first()

def create_user_if_not_admin(db: Session, telegram_id: str, **user_data) -> Optional[User]:
    """
    Create user only if telegram_id doesn't exist in admins table
    Returns User object or None if user is admin
    """
    # Check if telegram_id exists in admins
    admin = db.query(Admin).filter(Admin.telegram_id == telegram_id).first()
    if admin:
        print(f"Telegram ID {telegram_id} is an admin, skipping user creation")
        return None
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if existing_user:
        # Update last_activity
        existing_user.last_activity = datetime.now()
        db.commit()
        db.refresh(existing_user)
        return existing_user
    
    # Create new user with UUID
    user = User(
        id=str(uuid.uuid4()),
        telegram_id=telegram_id,
        last_activity=datetime.now(),
        **user_data
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def promote_user_to_admin(db: Session, telegram_id: str, promoted_by_admin_id: str, 
                          role: AdminRole = AdminRole.admin, **admin_data) -> Admin:
    """
    Promote a user to admin:
    1. Create admin record
    2. Delete user record
    3. Transfer chat history ownership
    """
    # Get user
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise ValueError(f"User with telegram_id {telegram_id} not found")
    
    # Check if already admin
    existing_admin = db.query(Admin).filter(Admin.telegram_id == telegram_id).first()
    if existing_admin:
        raise ValueError(f"User is already an admin")
    
    try:
        # Create admin record with UUID
        admin = Admin(
            id=str(uuid.uuid4()),
            telegram_id=user.telegram_id,
            telegram_username=user.username,
            telegram_first_name=user.first_name,
            telegram_last_name=user.last_name,
            telegram_photo_url=user.photo_url,
            full_name=user.full_name or f"{user.first_name} {user.last_name}".strip(),
            role=role,
            is_active=True,
            **admin_data
        )
        db.add(admin)
        db.flush()  # Get admin.id before deleting user
        
        # Transfer chat sessions ownership (if needed)
        # Update sessions where user was the participant
        for session in user.sessions:
            session.admin_id = admin.id
        
        # Delete user record
        db.delete(user)
        
        db.commit()
        db.refresh(admin)
        
        print(f"User {telegram_id} promoted to {role.value} by admin {promoted_by_admin_id}")
        return admin
        
    except Exception as e:
        db.rollback()
        raise Exception(f"Failed to promote user: {str(e)}")

def demote_admin_to_user(db: Session, telegram_id: str) -> User:
    """
    Demote admin to regular user (only for admin role, not super_admin)
    """
    admin = db.query(Admin).filter(Admin.telegram_id == telegram_id).first()
    if not admin:
        raise ValueError(f"Admin with telegram_id {telegram_id} not found")
    
    if admin.role == AdminRole.super_admin:
        raise ValueError("Cannot demote super_admin")
    
    try:
        # Create user record with UUID
        user = User(
            id=str(uuid.uuid4()),
            telegram_id=admin.telegram_id,
            username=admin.telegram_username,
            first_name=admin.telegram_first_name,
            last_name=admin.telegram_last_name,
            photo_url=admin.telegram_photo_url,
            full_name=admin.full_name,
            is_active=admin.is_active,
            last_activity=datetime.now()
        )
        db.add(user)
        db.flush()
        
        # Update chat sessions
        for session in admin.sessions:
            session.admin_id = None
        
        # Delete admin record
        db.delete(admin)
        
        db.commit()
        db.refresh(user)
        
        return user
        
    except Exception as e:
        db.rollback()
        raise Exception(f"Failed to demote admin: {str(e)}")