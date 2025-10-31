from sqlalchemy.orm import Session
from ..database.models import ChatSession, User, ChatMessage, Admin, SessionStatus
from datetime import datetime
from ..utils  import Helpers

class ChatService:
    """Service for chat-related business logic"""
    
    def get_chat_history(self, user_id, limit=50):
        """Get chat history for a user"""
        messages = self.session.query(ChatMessage)\
            .filter_by(user_id=user_id)\
            .order_by(ChatMessage.created_at.desc())\
            .limit(limit)\
            .all()
        
        return [{
            'id': msg.id,
            'message': msg.message,
            'response': msg.response,
            'created_at': Helpers.format_timestamp(msg.created_at),
            'is_resolved': msg.is_resolved
        } for msg in messages]
    
    def get_all_chats(self):
        """Get all chat sessions"""
        chats = self.session.query(ChatMessage)\
            .order_by(ChatMessage.created_at.desc())\
            .all()
        
        return [{
            'id': chat.id,
            'user_id': chat.user_id,
            'username': chat.user.username if chat.user else 'Unknown',
            'message': chat.message,
            'response': chat.response,
            'created_at': Helpers.format_timestamp(chat.created_at),
            'is_resolved': chat.is_resolved
        } for chat in chats]

    def get_chat_by_id(self, db: Session, chat_id: int):
        """Get chat session by ID"""
        return db.query(ChatSession).filter(ChatSession.id == chat_id).first()

    def close_chat_session(self, db: Session, session_id: int, admin_id: int = None, admin_role: str = None):
        """Close a chat session"""
        chat_session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        
        if not chat_session:
            return {"success": False, "message": "Chat session not found"}
        
        # Check if admin has access to this chat (if admin_id provided)
        if admin_id and admin_role == 'admin' and chat_session.admin_id != admin_id:
            return {"success": False, "message": "Access denied"}
        
        # Close the session
        chat_session.status = SessionStatus.closed
        chat_session.end_time = datetime.now()
        db.commit()
        db.refresh(chat_session)
        
        return {
            "success": True, 
            "message": "Chat session closed successfully",
            "session": chat_session
        }

    def get_user_chats(self, db: Session, user_id: int):
        """Get all chats for a specific user"""
        return db.query(ChatSession).filter(ChatSession.user_id == user_id).all()
    
    def get_admin_chat_sessions(self, db: Session, admin_id: int, status: str = None):
        """Get chat sessions for a specific admin"""
        query = db.query(ChatSession).filter(ChatSession.admin_id == admin_id)
        if status:
            query = query.filter(ChatSession.status == status)
        return query.all()
    
    def get_active_chat_sessions(self, db: Session, admin_id: int = None):
        """Get active chat sessions, optionally filtered by admin"""
        query = db.query(ChatSession).filter(ChatSession.status == SessionStatus.active)
        if admin_id:
            query = query.filter(ChatSession.admin_id == admin_id)
        return query.all()
    
    def send_chat_message(self, db: Session, session_id: int, admin_id: int, 
                         message_text: str, admin_role: str):
        """Send message to user in a chat session"""
        chat_session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        
        if not chat_session:
            return {"success": False, "message": "Session not found"}
        
        # Check access for regular admins
        if admin_role == 'admin' and chat_session.admin_id != admin_id:
            return {"success": False, "message": "Access denied"}
        
        # Create message record
        new_message = ChatMessage(
            user_id=chat_session.user_id,
            admin_id=admin_id,
            message=message_text,
            is_from_admin=True,
            timestamp=datetime.now()
        )
        
        db.add(new_message)
        db.commit()
        db.refresh(new_message)
        
        return {
            "success": True, 
            "message": "Message sent successfully",
            "chat_message": new_message
        }
    
    def get_chat_messages(self, db: Session, user_id: int, admin_id: int = None):
        """Get all messages for a user, optionally filtered by admin"""
        query = db.query(ChatMessage).filter(ChatMessage.user_id == user_id)
        
        # If admin_id provided, filter messages for this specific chat session
        if admin_id:
            query = query.filter(
                (ChatMessage.admin_id == admin_id) | (ChatMessage.admin_id == None)
            )
        
        return query.order_by(ChatMessage.timestamp).all()
    
    def get_session_messages(self, db: Session, session_id: int):
        """Get messages for a specific chat session"""
        # Get the session first
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        
        if not session:
            return []
        
        # Get messages for this user and admin combination
        query = db.query(ChatMessage).filter(
            ChatMessage.user_id == session.user_id
        )
        
        # Filter by admin if assigned
        if session.admin_id:
            query = query.filter(
                (ChatMessage.admin_id == session.admin_id) | 
                (ChatMessage.admin_id == None)
            )
        
        return query.order_by(ChatMessage.timestamp).all()
    
    def check_chat_access(self, db: Session, session_id: int, admin_id: int, admin_role: str):
        """Check if admin has access to a specific chat"""
        chat_session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        
        if not chat_session:
            return {"success": False, "message": "Chat session not found"}
        
        # Super admin has access to all chats
        if admin_role == 'super_admin':
            return {"success": True, "session": chat_session}
        
        # Regular admin can only access their assigned chats
        if chat_session.admin_id != admin_id:
            return {"success": False, "message": "Access denied. You can only view your assigned chats."}
        
        return {"success": True, "session": chat_session}
    
    def get_chat_statistics(self, db: Session, admin_id: int = None):
        """Get chat statistics"""
        stats = {
            "total_chats": db.query(ChatSession).count(),
            "active_chats": db.query(ChatSession).filter(
                ChatSession.status == SessionStatus.active
            ).count(),
            "closed_chats": db.query(ChatSession).filter(
                ChatSession.status == SessionStatus.closed
            ).count(),
            "unassigned_chats": db.query(ChatSession).filter(
                ChatSession.admin_id == None
            ).count()
        }
        
        # If admin_id provided, get their specific stats
        if admin_id:
            stats["my_chats"] = db.query(ChatSession).filter(
                ChatSession.admin_id == admin_id
            ).count()
            stats["my_active_chats"] = db.query(ChatSession).filter(
                ChatSession.admin_id == admin_id,
                ChatSession.status == SessionStatus.active
            ).count()
        
        return stats