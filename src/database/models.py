from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum, func, Text
from sqlalchemy.orm import relationship
from .connection import Base
import enum

class SessionStatus(enum.Enum):
    active = "active"
    closed = "closed"

class AdminRole(enum.Enum):
    super_admin = "super_admin"
    admin = "admin"  # admin is also an agent

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String(50), unique=True, nullable=False)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    photo_url = Column(String(500), nullable=True)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity = Column(DateTime(timezone=True), nullable=True)

    sessions = relationship("ChatSession", back_populates="user")
    messages = relationship("ChatMessage", back_populates="user")

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String(50), unique=True, nullable=False)
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
    user_id = Column(Integer, ForeignKey("users.id"))
    admin_id = Column(Integer, ForeignKey("admins.id"))
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    status = Column(Enum(SessionStatus), default=SessionStatus.active)

    user = relationship("User", back_populates="sessions")
    admin = relationship("Admin", back_populates="sessions")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    admin_id = Column(Integer, ForeignKey("admins.id"), nullable=True)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    is_from_admin = Column(Boolean, default=False)

    user = relationship("User", back_populates="messages")
    admin = relationship("Admin")

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