from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash, check_password_hash
from ..database.models import Admin, AdminRole
from datetime import datetime, timedelta
import jwt
import os
import hashlib
import hmac
from ..utils.jwt_helper import jwt_helper  # Add this import

class AuthService:
    def __init__(self):
        self.secret_key = os.getenv("SECRET_KEY", "your_secret_key")
        self.bot_token = os.getenv("BOT_TOKEN")
        self.token_expiry = int(os.getenv("TOKEN_EXPIRY_HOURS", 24))
        self.jwt_helper = jwt_helper  # Add JWT helper
    
    def verify_telegram_auth(self, auth_data):
        """Verify Telegram authentication data"""
        # Create a copy to avoid modifying original
        data_copy = auth_data.copy()
        check_hash = data_copy.pop('hash', None)
        
        if not check_hash:
            return {"success": False, "message": "No hash provided"}
        
        # Create data check string (only include non-empty values)
        data_check_arr = []
        for key, value in sorted(data_copy.items()):
            if value:  # Only include non-empty values
                data_check_arr.append(f"{key}={value}")
        
        data_check_string = '\n'.join(data_check_arr)
        
        print(f"Data check string: {data_check_string}")  # Debug
        print(f"Received hash: {check_hash}")  # Debug
        
        # Create secret key from bot token
        secret_key = hashlib.sha256(self.bot_token.encode()).digest()
        
        # Calculate hash
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        
        print(f"Calculated hash: {calculated_hash}")  # Debug
        
        if calculated_hash != check_hash:
            return {"success": False, "message": "Data verification failed"}
        
        # Check if auth data is not too old (within 86400 seconds = 24 hours)
        auth_date = int(data_copy.get('auth_date', 0))
        current_time = int(datetime.now().timestamp())
        if current_time - auth_date > 86400:
            return {"success": False, "message": "Authentication data is too old"}
        
        return {"success": True, "data": data_copy}
    
    def authenticate_admin_telegram(self, db: Session, telegram_data):
        """Authenticate admin using Telegram data"""
        # Verify Telegram authentication
        verification = self.verify_telegram_auth(telegram_data.copy())
        if not verification['success']:
            return verification
        
        telegram_id = str(telegram_data.get('id'))
        
        # Find admin by Telegram ID
        admin = db.query(Admin).filter(
            Admin.telegram_id == telegram_id,
            Admin.is_active == True
        ).first()
        
        if not admin:
            return {"success": False, "message": "Admin account not found or inactive"}
        
        # Update admin info from Telegram data
        admin.telegram_username = telegram_data.get('username')
        admin.telegram_first_name = telegram_data.get('first_name')
        admin.telegram_last_name = telegram_data.get('last_name')
        admin.telegram_photo_url = telegram_data.get('photo_url')
        admin.last_login = datetime.now()
        
        # Update full name if not set or different
        telegram_full_name = f"{telegram_data.get('first_name', '')} {telegram_data.get('last_name', '')}".strip()
        if not admin.full_name or admin.full_name != telegram_full_name:
            admin.full_name = telegram_full_name
        
        db.commit()
        
        # Generate JWT tokens instead of simple token
        access_token = self.jwt_helper.generate_access_token(
            admin_id=admin.id,
            role=admin.role.value if hasattr(admin.role, 'value') else admin.role
        )
        
        refresh_token = self.jwt_helper.generate_refresh_token(
            admin_id=admin.id
        )
        
        return {
            "success": True,
            "message": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": self.jwt_helper.access_token_expires,
            "admin": self._serialize_admin(admin)
        }
    
    def create_admin_telegram(self, db: Session, telegram_id: str, full_name: str, role: str = "admin"):
        """Create admin account with Telegram ID"""
        # Check if admin already exists
        existing_admin = db.query(Admin).filter(Admin.telegram_id == telegram_id).first()
        if existing_admin:
            return {"success": False, "message": "Admin with this Telegram ID already exists"}
        
        # Create new admin
        new_admin = Admin(
            telegram_id=telegram_id,
            full_name=full_name,
            role=AdminRole.admin if role == "admin" else AdminRole.super_admin,
            is_active=True
        )
        
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)
        
        return {
            "success": True,
            "message": "Admin created successfully",
            "admin": self._serialize_admin(new_admin)
        }
    
    def generate_token(self, admin_id: int):
        """Generate JWT token for admin"""
        payload = {
            "admin_id": admin_id,
            "exp": datetime.utcnow() + timedelta(hours=self.token_expiry),
            "iat": datetime.utcnow()
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        return token
    
    def verify_token(self, token: str):
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return {"success": True, "admin_id": payload["admin_id"]}
        except jwt.ExpiredSignatureError:
            return {"success": False, "message": "Token has expired"}
        except jwt.InvalidTokenError:
            return {"success": False, "message": "Invalid token"}
    
    def get_admin_by_id(self, db: Session, admin_id: int):
        """Get admin by ID"""
        return db.query(Admin).filter(Admin.id == admin_id, Admin.is_active == True).first()
    
    def deactivate_admin(self, db: Session, admin_id: int):
        """Deactivate admin account"""
        admin = db.query(Admin).filter(Admin.id == admin_id).first()
        
        if not admin:
            return {"success": False, "message": "Admin not found"}
        
        admin.is_active = False
        db.commit()
        
        return {"success": True, "message": "Admin account deactivated"}
    
    def update_admin_profile(self, db: Session, admin_id: int, full_name: str, division: str = None):
        """Update admin profile information"""
        admin = db.query(Admin).filter(Admin.id == admin_id).first()
        
        if not admin:
            return {"success": False, "message": "Admin not found"}
        
        if not full_name or not full_name.strip():
            return {"success": False, "message": "Full name is required"}
        
        admin.full_name = full_name.strip()
        
        # Only update division for regular admins
        if admin.role == AdminRole.admin and division is not None:
            admin.division = division.strip()
        
        db.commit()
        db.refresh(admin)
        
        return {
            "success": True,
            "message": "Profile updated successfully",
            "admin": self._serialize_admin(admin)
        }
    
    def toggle_admin_availability(self, db: Session, admin_id: str):
        """Toggle admin availability for chat assignment"""
        admin = db.query(Admin).filter(Admin.id == admin_id).first()
        
        if not admin:
            return {
                'success': False,
                'message': 'Admin not found'
            }
        
        # Only regular admins can change availability
        if admin.role != AdminRole.admin:
            return {
                'success': False,
                'message': 'Only regular admins can change availability status'
            }
        
        admin.is_available = not admin.is_available
        db.commit()
        db.refresh(admin)
        
        status = "available" if admin.is_available else "unavailable"
        
        return {
            "success": True,
            "message": f"You are now {status} for new chat assignments",
            "data": {
                "is_available": admin.is_available,
                "admin": self._serialize_admin(admin)
            }
        }
    
    def authenticate_admin_api(self, db: Session, telegram_id: str):
        """
        Authenticate admin for API access (returns JWT tokens)
        
        Args:
            db: Database session
            telegram_id: Admin's Telegram ID
            
        Returns:
            Dictionary with tokens and admin info
        """
        admin = db.query(Admin).filter(
            Admin.telegram_id == telegram_id,
            Admin.is_active == True
        ).first()
        
        if not admin:
            return {
                "success": False,
                "message": "Admin not found or inactive"
            }
        
        # Update last login
        admin.last_login = datetime.utcnow()
        db.commit()
        
        # Generate JWT tokens
        access_token = self.jwt_helper.generate_access_token(
            admin_id=admin.id,
            role=admin.role.value
        )
        
        refresh_token = self.jwt_helper.generate_refresh_token(
            admin_id=admin.id
        )
        
        return {
            "success": True,
            "message": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": self.jwt_helper.access_token_expires,
            "admin": self._serialize_admin(admin)
        }
    
    def refresh_access_token(self, refresh_token: str, db: Session):
        """
        Generate new access token using refresh token
        
        Args:
            refresh_token: Refresh token
            db: Database session
            
        Returns:
            Dictionary with new access token
        """
        # Verify refresh token
        result = self.jwt_helper.verify_token(refresh_token)
        
        if not result['success']:
            return {
                "success": False,
                "message": result['message']
            }
        
        payload = result['payload']
        
        # Check token type
        if payload.get('token_type') != 'refresh':
            return {
                "success": False,
                "message": "Invalid token type"
            }
        
        # Get admin
        admin_id = payload.get('admin_id')
        admin = db.query(Admin).filter(
            Admin.id == admin_id,
            Admin.is_active == True
        ).first()
        
        if not admin:
            return {
                "success": False,
                "message": "Admin not found or inactive"
            }
        
        # Generate new access token
        access_token = self.jwt_helper.generate_access_token(
            admin_id=admin.id,
            role=admin.role.value
        )
        
        return {
            "success": True,
            "message": "Token refreshed",
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": self.jwt_helper.access_token_expires
        }
    
    def _serialize_admin(self, admin):
        """Helper function to serialize admin object"""
        return {
            "id": admin.id,
            "telegram_id": admin.telegram_id,
            "telegram_username": admin.telegram_username,
            "full_name": admin.full_name,
            "role": admin.role.value if admin.role else None,
            "is_active": admin.is_active,
            "division": admin.division,
            "is_available": admin.is_available,
            "created_at": admin.created_at.isoformat() if admin.created_at else None,
            "last_login": admin.last_login.isoformat() if admin.last_login else None
        }