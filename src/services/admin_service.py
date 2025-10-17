from sqlalchemy.orm import Session
from ..database.models import User, ChatSession

def get_all_users(db: Session):
    return db.query(User).all()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_chat_history(db: Session, user_id: int):
    return db.query(ChatSession).filter(ChatSession.user_id == user_id).all()

def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return True
    return False

def get_all_chat_sessions(db: Session):
    return db.query(ChatSession).all()