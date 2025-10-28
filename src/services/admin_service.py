from sqlalchemy.orm import Session
from ..database.models import User, ChatSession, Admin, ChatMessage, SessionStatus
from datetime import datetime

class AdminService:
    """Service for admin-related business logic"""
    
    def get_all_admins(self, db: Session):
        """Get all admins"""
        return db.query(Admin).all()
    
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