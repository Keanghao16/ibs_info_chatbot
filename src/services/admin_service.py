from sqlalchemy.orm import Session
from ..database.models import User, ChatSession, Admin, ChatMessage, SessionStatus
from datetime import datetime

class AdminService:
    """Service for admin-related business logic"""
    
    def get_all_users(self, db: Session):
        """Get all users"""
        return db.query(User).all()

    def get_user_by_id(self, db: Session, user_id: int):
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()

    def get_chat_history(self, db: Session, user_id: int):
        """Get chat history for a specific user"""
        return db.query(ChatSession).filter(ChatSession.user_id == user_id).all()

    def delete_user(self, db: Session, user_id: int):
        """Delete a user"""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            db.delete(user)
            db.commit()
            return {"success": True, "message": "User deleted successfully"}
        return {"success": False, "message": "User not found"}

    def get_all_chat_sessions(self, db: Session):
        """Get all chat sessions"""
        return db.query(ChatSession).all()
    
    def get_admin_chat_sessions(self, db: Session, admin_id: int, status: str = None):
        """Get chat sessions for a specific admin"""
        query = db.query(ChatSession).filter(ChatSession.admin_id == admin_id)
        if status:
            query = query.filter(ChatSession.status == status)
        return query.all()
    
    def get_active_chat_sessions(self, db: Session, admin_id: int = None):
        """Get active chat sessions, optionally filtered by admin"""
        query = db.query(ChatSession).filter(ChatSession.status == 'active')
        if admin_id:
            query = query.filter(ChatSession.admin_id == admin_id)
        return query.all()
    
    def toggle_admin_status(self, db: Session, admin_id: int, current_admin_id: int):
        """Toggle admin active status"""
        admin = db.query(Admin).filter(Admin.id == admin_id).first()
        
        if not admin:
            return {"success": False, "message": "Admin not found"}
        
        # Don't allow deactivating yourself
        if admin.id == current_admin_id:
            return {"success": False, "message": "You cannot deactivate your own account"}
        
        admin.is_active = not admin.is_active
        db.commit()
        db.refresh(admin)
        
        status = "activated" if admin.is_active else "deactivated"
        return {
            "success": True, 
            "message": f"Admin {status} successfully",
            "is_active": admin.is_active
        }
    
    def toggle_admin_availability(self, db: Session, admin_id: int):
        """Toggle admin availability for taking new chats"""
        admin = db.query(Admin).filter(Admin.id == admin_id).first()
        
        if not admin:
            return {"success": False, "message": "Admin not found"}
        
        admin.is_available = not admin.is_available
        db.commit()
        db.refresh(admin)
        
        status = "available" if admin.is_available else "unavailable"
        return {
            "success": True,
            "status": status,
            "is_available": admin.is_available
        }
    
    def close_chat_session(self, db: Session, session_id: int, admin_id: int, admin_role: str):
        """Close a chat session"""
        chat_session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        
        if not chat_session:
            return {"success": False, "message": "Chat session not found"}
        
        # Check if admin has access to this chat
        if admin_role == 'admin' and chat_session.admin_id != admin_id:
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
    
    def get_dashboard_stats(self, db: Session, admin_id: int = None, admin_role: str = None):
        """Get dashboard statistics"""
        stats = {
            "users_count": db.query(User).count(),
            "chats_count": db.query(ChatSession).count(),
            "active_chats_count": db.query(ChatSession).filter(
                ChatSession.status == 'active'
            ).count()
        }
        
        # If admin role, get their specific stats
        if admin_role == 'admin' and admin_id:
            stats["admin_chats_count"] = db.query(ChatSession).filter(
                ChatSession.admin_id == admin_id
            ).count()
            stats["admin_active_chats"] = db.query(ChatSession).filter(
                ChatSession.admin_id == admin_id,
                ChatSession.status == 'active'
            ).count()
        
        return {"success": True, "stats": stats}
    
    def get_all_admins(self, db: Session):
        """Get all admins"""
        return db.query(Admin).all()
    
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
    
    def get_chat_messages(self, db: Session, user_id: int):
        """Get all messages for a user"""
        return db.query(ChatMessage).filter(
            ChatMessage.user_id == user_id
        ).order_by(ChatMessage.timestamp).all()
    
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