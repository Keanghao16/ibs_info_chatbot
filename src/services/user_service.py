from sqlalchemy.orm import Session
from ..database.models import User

def get_all_users(db: Session):
    return db.query(User).all()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_telegram_id(db: Session, telegram_id: str):
    """Get user by Telegram ID"""
    return db.query(User).filter(User.telegram_id == telegram_id).first()

def find_or_create_user(db: Session, telegram_user):
    """Find existing user or create new one from Telegram user object"""
    existing_user = get_user_by_telegram_id(db, str(telegram_user.id))
    
    if existing_user:
        # Update user info if changed
        updated = False
        full_name = telegram_user.full_name or f"{telegram_user.first_name} {telegram_user.last_name or ''}".strip()
        
        if existing_user.full_name != full_name:
            existing_user.full_name = full_name
            updated = True
        if existing_user.username != telegram_user.username:
            existing_user.username = telegram_user.username
            updated = True
        if not existing_user.is_active:
            existing_user.is_active = True
            updated = True
            
        if updated:
            db.commit()
            db.refresh(existing_user)
        
        return existing_user
    else:
        # Create new user
        user_data = {
            "telegram_id": str(telegram_user.id),
            "full_name": telegram_user.full_name or f"{telegram_user.first_name} {telegram_user.last_name or ''}".strip(),
            "username": telegram_user.username,
            "is_active": True
        }
        return create_user(db, user_data)

def create_user(db: Session, user_data: dict):
    new_user = User(**user_data)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def update_user(db: Session, user_id: int, user_data: dict):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        for key, value in user_data.items():
            setattr(user, key, value)
        db.commit()
        db.refresh(user)
    return user

def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    return user

def deactivate_user(db: Session, telegram_id: str):
    """Deactivate user by Telegram ID"""
    user = get_user_by_telegram_id(db, telegram_id)
    if user:
        user.is_active = False
        db.commit()
        db.refresh(user)
    return user