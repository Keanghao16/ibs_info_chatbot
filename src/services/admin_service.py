from sqlalchemy.orm import Session
from ..database.models import User, ChatSession, Admin, ChatMessage, SessionStatus, AdminRole
from datetime import datetime
import uuid

class AdminService:
    """Service for admin-related business logic"""
    
    def get_all_admins(self, db: Session):
        """Get all admins"""
        return db.query(Admin).all()
    
    def get_admin_by_id(self, db: Session, admin_id: str):
        """Get admin by UUID"""
        return db.query(Admin).filter(Admin.id == admin_id).first()
    
    def create_admin(self, db: Session, telegram_id: str, full_name: str, role: str = 'admin', division: str = None):
        """Create new admin using Telegram ID"""
        try:
            # Check if admin already exists
            existing = db.query(Admin).filter(Admin.telegram_id == telegram_id).first()
            if existing:
                return {"success": False, "message": "Admin with this Telegram ID already exists"}
            
            # Validate role
            if role not in ['admin', 'super_admin']:
                return {"success": False, "message": "Invalid role"}
            
            # Create admin
            admin = Admin(
                id=str(uuid.uuid4()),
                telegram_id=telegram_id,
                full_name=full_name,
                role=AdminRole[role],
                is_active=True,
                is_available=True if role == 'admin' else None,
                division=division if role == 'admin' else None
            )
            
            db.add(admin)
            db.commit()
            db.refresh(admin)
            
            return {
                "success": True,
                "message": "Admin created successfully",
                "admin": self._serialize_admin(admin)
            }
        except Exception as e:
            db.rollback()
            return {"success": False, "message": f"Error creating admin: {str(e)}"}
    
    def toggle_admin_status(self, db: Session, admin_id: str, current_admin_id: str):
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
    
    def toggle_admin_availability(self, db: Session, admin_id: str):
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
            "message": f"Admin is now {status}",
            "status": status,
            "is_available": admin.is_available
        }
    
    def update_admin_profile(self, db: Session, admin_id: str, full_name: str, division: str = None, role: str = None):
        """Update admin profile"""
        admin = db.query(Admin).filter(Admin.id == admin_id).first()
        
        if not admin:
            return {"success": False, "message": "Admin not found"}
        
        if not full_name or not full_name.strip():
            return {"success": False, "message": "Full name is required"}
        
        if len(full_name.strip()) < 3:
            return {"success": False, "message": "Full name must be at least 3 characters long"}
        
        try:
            # Update full name
            admin.full_name = full_name.strip()
            
            # Update role if changed
            if role and role in ['admin', 'super_admin']:
                old_role = admin.role
                new_role = AdminRole[role]
                
                # Update role
                admin.role = new_role
                
                # Update division based on new role
                if new_role == AdminRole.admin:
                    admin.division = division.strip() if division and division.strip() else None
                else:  # super_admin
                    admin.division = None
                
                # Clear is_available for super_admin
                if new_role == AdminRole.super_admin:
                    admin.is_available = None
                elif old_role == AdminRole.super_admin and new_role == AdminRole.admin:
                    # Converting from super_admin to admin, set default availability
                    admin.is_available = True
            else:
                # Role not changed, only update division if admin
                if admin.role == AdminRole.admin:
                    admin.division = division.strip() if division and division.strip() else None
            
            db.commit()
            db.refresh(admin)
            
            return {
                "success": True,
                "message": "Admin profile updated successfully",
                "admin": self._serialize_admin(admin)
            }
        except Exception as e:
            db.rollback()
            return {"success": False, "message": f"Error updating admin: {str(e)}"}
    
    def delete_admin(self, db: Session, admin_id: str, current_admin_id: str):
        """Delete admin account"""
        # Prevent self-deletion
        if admin_id == current_admin_id:
            return {"success": False, "message": "You cannot delete your own account"}
        
        admin = db.query(Admin).filter(Admin.id == admin_id).first()
        
        if not admin:
            return {"success": False, "message": "Admin not found"}
        
        try:
            # Store admin name before deletion
            admin_name = admin.full_name
            
            # Delete admin
            db.delete(admin)
            db.commit()
            
            return {
                "success": True,
                "message": f"Admin {admin_name} deleted successfully"
            }
        except Exception as e:
            db.rollback()
            return {"success": False, "message": f"Error deleting admin: {str(e)}"}
    
    def get_admin_statistics(self, db: Session):
        """Get admin statistics"""
        try:
            admins = self.get_all_admins(db)
            
            stats = {
                "total_admins": len(admins),
                "super_admins": len([a for a in admins if a.role == AdminRole.super_admin]),
                "regular_admins": len([a for a in admins if a.role == AdminRole.admin]),
                "active_admins": len([a for a in admins if a.is_active]),
                "inactive_admins": len([a for a in admins if not a.is_active]),
                "available_agents": len([a for a in admins if a.role == AdminRole.admin and a.is_available and a.is_active]),
                "unavailable_agents": len([a for a in admins if a.role == AdminRole.admin and not a.is_available and a.is_active])
            }
            
            return {"success": True, "stats": stats}
        except Exception as e:
            return {"success": False, "message": f"Error fetching statistics: {str(e)}"}
    
    def get_admin_info(self, db: Session, admin_id: str):
        """Get formatted admin info for templates"""
        admin = self.get_admin_by_id(db, admin_id)
        
        if not admin:
            return None
        
        return self._serialize_admin(admin)
    
    def _serialize_admin(self, admin):
        """Convert admin model to dictionary"""
        return {
            'id': admin.id,
            'telegram_id': admin.telegram_id,
            'telegram_username': admin.telegram_username,
            'telegram_first_name': admin.telegram_first_name,
            'telegram_last_name': admin.telegram_last_name,
            'telegram_photo_url': admin.telegram_photo_url,
            'full_name': admin.full_name,
            'role': admin.role.value if admin.role else 'admin',
            'is_active': admin.is_active,
            'division': admin.division,
            'is_available': admin.is_available,
            'last_login': admin.last_login.strftime('%Y-%m-%d %H:%M:%S') if admin.last_login else None,
            'created_at': admin.created_at.strftime('%Y-%m-%d %H:%M:%S') if admin.created_at else None
        }