from sqlalchemy.orm import Session
from ..database.models import Admin, AdminRole
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class AdminService:
    """Service for admin-related business logic"""
    
    @staticmethod
    def get_all_admins(db: Session, page: int = 1, per_page: int = 10, search: str = None, role: str = None, is_active: bool = None, is_available: bool = None):
        """Get paginated admins with filters"""
        query = db.query(Admin)
        
        # Apply filters
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Admin.full_name.ilike(search_term)) |
                (Admin.telegram_username.ilike(search_term))
            )
        
        if role:
            query = query.filter(Admin.role == role)
        
        if is_active is not None:
            query = query.filter(Admin.is_active == is_active)
        
        if is_available is not None:
            query = query.filter(Admin.is_available == is_available)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        admins = query.order_by(Admin.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
        
        return {
            'admins': admins,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }
    
    @staticmethod
    def get_admin_by_id(db: Session, admin_id: str):
        """Get admin by ID (UUID)"""
        return db.query(Admin).filter(Admin.id == admin_id).first()
    
    @staticmethod
    def get_admin_by_telegram_id(db: Session, telegram_id: str):
        """Get admin by Telegram ID"""
        return db.query(Admin).filter(Admin.telegram_id == telegram_id).first()
    
    #  ADD THIS METHOD
    @staticmethod
    def get_admin_by_username(db: Session, username: str):
        """Get admin by username (Telegram username)"""
        return db.query(Admin).filter(Admin.telegram_username == username).first()
    
    @staticmethod
    def create_admin(db: Session, admin_data: dict):
        """Create new admin"""
        # Handle role conversion
        if 'role' in admin_data:
            if isinstance(admin_data['role'], str):
                admin_data['role'] = AdminRole.super_admin if admin_data['role'] == 'super_admin' else AdminRole.admin
        
        # Create admin
        admin = Admin(
            telegram_id=admin_data.get('telegram_id'),
            telegram_username=admin_data.get('username'),  # Map username to telegram_username
            full_name=admin_data.get('full_name'),
            role=admin_data.get('role', AdminRole.admin),
            division=admin_data.get('division'),
            is_active=True,
            is_available=True if admin_data.get('role') == AdminRole.admin else None,
            created_at=datetime.utcnow()
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        return admin
    
    @staticmethod
    def update_admin(db: Session, admin_id: str, update_data: dict):
        """Update admin"""
        admin = db.query(Admin).filter(Admin.id == admin_id).first()
        if admin:
            # Handle role conversion
            if 'role' in update_data:
                if isinstance(update_data['role'], str):
                    update_data['role'] = AdminRole.super_admin if update_data['role'] == 'super_admin' else AdminRole.admin
            
            for key, value in update_data.items():
                setattr(admin, key, value)
            
            db.commit()
            db.refresh(admin)
        return admin
    
    @staticmethod
    def delete_admin(db: Session, admin_id: str):
        """Delete admin"""
        admin = db.query(Admin).filter(Admin.id == admin_id).first()
        if admin:
            db.delete(admin)
            db.commit()
        return True
    
    @staticmethod
    def toggle_availability(db: Session, admin_id: str):
        """Toggle admin availability"""
        admin = db.query(Admin).filter(Admin.id == admin_id).first()
        if admin:
            admin.is_available = not admin.is_available
            db.commit()
            db.refresh(admin)
        return admin
    
    @staticmethod
    def toggle_admin_status(db: Session, admin_id: str, current_admin_id: str):
        """Toggle admin active status (super admin only)"""
        # Prevent self-deactivation
        if admin_id == current_admin_id:
            return {
                'success': False,
                'message': 'You cannot deactivate your own account'
            }
        
        admin = db.query(Admin).filter(Admin.id == admin_id).first()
        if not admin:
            return {
                'success': False,
                'message': 'Admin not found'
            }
        
        admin.is_active = not admin.is_active
        db.commit()
        db.refresh(admin)
        
        status = "activated" if admin.is_active else "deactivated"
        
        return {
            'success': True,
            'message': f'Admin {status} successfully',
            'is_active': admin.is_active
        }
    
    @staticmethod
    def get_admin_statistics(db: Session):
        """Get admin statistics"""
        total_admins = db.query(Admin).count()
        active_admins = db.query(Admin).filter(Admin.is_active == True).count()
        available_admins = db.query(Admin).filter(Admin.is_available == True).count()
        super_admins = db.query(Admin).filter(Admin.role == AdminRole.super_admin).count()
        regular_admins = db.query(Admin).filter(Admin.role == AdminRole.admin).count()  # ✅ Added
        
        return {
            'total_admins': total_admins,
            'active_admins': active_admins,
            'available_admins': available_admins,
            'super_admins': super_admins,
            'regular_admins': regular_admins,  # ✅ Added
            'online_now': 0  # TODO: Implement real-time tracking
        }
    
    @staticmethod
    def get_admin_info(db: Session, admin_id: str):
        """Get detailed admin information"""
        admin = db.query(Admin).filter(Admin.id == admin_id).first()
        
        if not admin:
            return None
        
        return {
            'id': admin.id,
            'telegram_id': admin.telegram_id,
            'telegram_username': admin.telegram_username,
            'full_name': admin.full_name,
            'role': admin.role.value if hasattr(admin.role, 'value') else admin.role,
            'is_active': admin.is_active,
            'is_available': admin.is_available,
            'division': admin.division,
            'created_at': admin.created_at,
            'last_login': admin.last_login
        }
    
    @staticmethod
    def demote_to_user(db: Session, admin_id: str):
        """Demote an admin to a regular user"""
        from ..database.models import User, ChatSession
        import uuid
        
        # Get the admin
        admin = db.query(Admin).filter(Admin.id == admin_id).first()
        if not admin:
            return None
        
        # Create a user record with admin's data
        user = User(
            id=str(uuid.uuid4()),
            telegram_id=int(admin.telegram_id),
            username=admin.telegram_username,
            first_name=admin.full_name.split()[0] if admin.full_name else admin.telegram_username,
            last_name=' '.join(admin.full_name.split()[1:]) if admin.full_name and len(admin.full_name.split()) > 1 else None,
            photo_url=admin.telegram_photo_url,
            registration_date=admin.created_at,
            last_activity=admin.last_login,
            is_bot=False,
            is_premium=False
        )
        
        # Unassign all chat sessions from this admin
        db.query(ChatSession).filter(ChatSession.admin_id == admin_id).update(
            {ChatSession.admin_id: None},
            synchronize_session=False
        )
        
        # Delete the admin record
        db.delete(admin)
        db.flush()  # Ensure admin is deleted before adding user
        
        # Add the new user
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user