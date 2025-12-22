from sqlalchemy.orm import Session
from ..database.models import ChatSession, User, ChatMessage, Admin, SessionStatus
from datetime import datetime
from ..utils import Helpers

class ChatService:
    """Service for chat-related business logic"""
    
    @staticmethod
    def get_all_sessions(db: Session, page: int = 1, per_page: int = 10, status: str = None, admin_id: str = None, user_id: str = None):
        """Get paginated chat sessions"""
        query = db.query(ChatSession)
        
        # Apply filters
        if status:
            #  Convert string to enum
            status_map = {
                'waiting': SessionStatus.waiting,
                'active': SessionStatus.active,
                'closed': SessionStatus.closed
            }
            enum_status = status_map.get(status.lower())
            if enum_status:
                query = query.filter(ChatSession.status == enum_status)
        
        #  admin_id and user_id are UUIDs (strings)
        if admin_id:
            query = query.filter(ChatSession.admin_id == admin_id)
        if user_id:
            query = query.filter(ChatSession.user_id == user_id)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        sessions = query.order_by(ChatSession.start_time.desc()).offset((page - 1) * per_page).limit(per_page).all()
        
        return {
            'sessions': sessions,
            'total': total,
            'page': page,
            'per_page': per_page
        }
    
    @staticmethod
    def get_session_by_id(db: Session, session_id: int):
        """Get chat session by ID (INTEGER, not UUID)"""
        return db.query(ChatSession).filter(ChatSession.id == session_id).first()
    
    @staticmethod
    def create_session(db: Session, session_data: dict):
        """Create new chat session"""
        #  Convert string status to enum
        if 'status' in session_data:
            if isinstance(session_data['status'], str):
                status_map = {
                    'waiting': SessionStatus.waiting,
                    'active': SessionStatus.active,
                    'closed': SessionStatus.closed
                }
                session_data['status'] = status_map.get(session_data['status'].lower(), SessionStatus.waiting)
        else:
            session_data['status'] = SessionStatus.waiting
        
        #  Ensure user_id is string (UUID) - KEEP THIS
        if 'user_id' in session_data:
            session_data['user_id'] = str(session_data['user_id'])
        
        #  DO NOT convert session ID - it's auto-generated as INTEGER
        session = ChatSession(**session_data)
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
    
    @staticmethod
    def assign_to_admin(db: Session, session_id: int, admin_id: str):
        """Assign chat to admin"""
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if session:
            session.admin_id = admin_id  #  admin_id is UUID string
            session.status = SessionStatus.active
            db.commit()
            db.refresh(session)
        return session
    
    @staticmethod
    def close_session(db: Session, session_id: int):
        """Close chat session"""
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if session:
            session.status = SessionStatus.closed
            session.end_time = datetime.utcnow()
            db.commit()
            db.refresh(session)
        return session
    
    @staticmethod
    def get_session_messages(db: Session, session_id: int):
        """Get all messages from a session"""
        return db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.timestamp).all()
    
    @staticmethod
    def create_message(db: Session, message_data: dict):
        """Create new message"""
        # Ensure session_id is included
        if 'session_id' not in message_data:
            raise ValueError("session_id is required")
        
        message = ChatMessage(**message_data)
        db.add(message)
        db.commit()
        db.refresh(message)
        return message
    
    @staticmethod
    def get_chat_statistics(db: Session):
        """Get chat statistics"""
        total_sessions = db.query(ChatSession).count()
        active_sessions = db.query(ChatSession).filter(ChatSession.status == SessionStatus.active).count()
        waiting_sessions = db.query(ChatSession).filter(ChatSession.status == SessionStatus.waiting).count()
        closed_sessions = db.query(ChatSession).filter(ChatSession.status == SessionStatus.closed).count()
        total_messages = db.query(ChatMessage).count()
        
        return {
            'total_sessions': total_sessions,
            'active_sessions': active_sessions,
            'waiting_sessions': waiting_sessions,
            'closed_sessions': closed_sessions,
            'total_messages': total_messages,
            'average_response_time': 0.0,  # TODO: Calculate
            'average_session_duration': 0.0  # TODO: Calculate
        }