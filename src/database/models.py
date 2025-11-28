from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum, func, Text, event, text, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.mysql import CHAR
from .connection import Base
import enum
import uuid
from datetime import datetime

class SessionStatus(enum.Enum):
    waiting = "waiting"
    active = "active"
    closed = "closed"

class AdminRole(enum.Enum):
    super_admin = "super_admin"
    admin = "admin"

class User(Base):
    __tablename__ = 'users'
    
    # ✅ FIX: Change from Integer to CHAR(36) for UUID
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    
    # Additional columns
    language_code = Column(String(10), nullable=True)
    is_bot = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    registration_date = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, nullable=True)
    
    # Computed property
    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or self.username or f"User {self.telegram_id}"

    sessions = relationship("ChatSession", back_populates="user")
    messages = relationship("ChatMessage", back_populates="user")


class Admin(Base):
    __tablename__ = "admins"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    telegram_id = Column(String(50), unique=True, nullable=False, index=True)
    telegram_username = Column(String(255), nullable=True)
    telegram_first_name = Column(String(255), nullable=True)
    telegram_last_name = Column(String(255), nullable=True)
    telegram_photo_url = Column(String(500), nullable=True)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(AdminRole), default=AdminRole.admin)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Agent-related fields (for admin role)
    division = Column(String(100), nullable=True)
    is_available = Column(Boolean, default=True)
    
    # Relationships
    sessions = relationship("ChatSession", back_populates="admin")


class ChatSession(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(CHAR(36), ForeignKey("users.id"))  # ✅ UUID
    admin_id = Column(CHAR(36), ForeignKey("admins.id"), nullable=True)  # ✅ UUID
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    status = Column(Enum(SessionStatus), default=SessionStatus.active)

    user = relationship("User", back_populates="sessions")
    admin = relationship("Admin", back_populates="sessions")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)  # ✅ ADD THIS
    user_id = Column(CHAR(36), ForeignKey("users.id"))  # ✅ UUID
    admin_id = Column(CHAR(36), ForeignKey("admins.id"), nullable=True)  # ✅ UUID
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    is_from_admin = Column(Boolean, default=False)

    user = relationship("User", back_populates="messages")
    admin = relationship("Admin")
    session = relationship("ChatSession")  # ✅ ADD THIS


class SystemSettings(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    # General Settings
    system_name = Column(String(255), default="IBS Info Chatbot")
    welcome_message = Column(Text, nullable=True)
    support_email = Column(String(255), nullable=True)
    max_chat_duration = Column(Integer, default=60)  # minutes
    auto_assign_chats = Column(Boolean, default=True)
    maintenance_mode = Column(Boolean, default=False)
    
    # Bot Settings
    bot_username = Column(String(255), nullable=True)
    response_timeout = Column(Integer, default=30)  # seconds
    offline_message = Column(Text, nullable=True)
    enable_file_uploads = Column(Boolean, default=True)
    enable_typing_indicator = Column(Boolean, default=True)
    
    # Notification Settings
    email_notifications = Column(Boolean, default=False)
    notify_new_user = Column(Boolean, default=True)
    notify_new_chat = Column(Boolean, default=True)
    notify_unassigned_chat = Column(Boolean, default=True)
    notification_email = Column(String(255), nullable=True)
    
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class FAQCategory(Base):
    __tablename__ = "faq_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # Display name
    slug = Column(String(100), unique=True, nullable=False)  # URL-friendly identifier
    description = Column(Text, nullable=True)
    icon = Column(String(50), nullable=True)  # Emoji or icon class
    is_active = Column(Boolean, default=True)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship
    faqs = relationship("FAQ", back_populates="faq_category", cascade="all, delete-orphan")

class FAQ(Base):
    __tablename__ = "faqs"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    category_id = Column(Integer, ForeignKey('faq_categories.id'), nullable=False)  # Foreign key to FAQCategory
    is_active = Column(Boolean, default=True)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship
    faq_category = relationship("FAQCategory", back_populates="faqs")

# Add these event listeners at the end of the file

@event.listens_for(User, 'before_insert')
@event.listens_for(User, 'before_update')
def check_user_telegram_id_not_in_admins(mapper, connection, target):
    """Prevent telegram_id from existing in both users and admins tables"""
    if target.telegram_id:
        result = connection.execute(
            text("SELECT 1 FROM admins WHERE telegram_id = :telegram_id LIMIT 1"),
            {"telegram_id": target.telegram_id}
        ).first()
        if result:
            raise IntegrityError(
                f"Telegram ID {target.telegram_id} already exists as admin",
                params=None,
                orig=None
            )

@event.listens_for(Admin, 'before_insert')
@event.listens_for(Admin, 'before_update')
def check_admin_telegram_id_not_in_users(mapper, connection, target):
    """Prevent telegram_id from existing in both users and admins tables"""
    if target.telegram_id:
        result = connection.execute(
            text("SELECT 1 FROM users WHERE telegram_id = :telegram_id LIMIT 1"),
            {"telegram_id": target.telegram_id}
        ).first()
        if result:
            raise IntegrityError(
                f"Telegram ID {target.telegram_id} already exists as user",
                params=None,
                orig=None
            )