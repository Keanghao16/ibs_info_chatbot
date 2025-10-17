from sqlalchemy.orm import Session
from ..database.models import ChatSession, User
from datetime import datetime

def get_chat_history(user_id: int, db: Session):
    return db.query(ChatSession).filter(ChatSession.user_id == user_id).all()

def get_all_chats(db: Session):
    return db.query(ChatSession).all()

def get_chat_by_id(chat_id: int, db: Session):
    return db.query(ChatSession).filter(ChatSession.id == chat_id).first()

def close_chat_session(chat_id: int, db: Session):
    chat_session = db.query(ChatSession).filter(ChatSession.id == chat_id).first()
    if chat_session:
        chat_session.end_time = datetime.now()
        chat_session.status = "closed"
        db.commit()
        return chat_session
    return None

def get_user_chats(user_id: int, db: Session):
    return db.query(ChatSession).filter(ChatSession.user_id == user_id).all()