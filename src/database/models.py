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
    full_name = Column(String(255))
    username = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sessions = relationship("ChatSession", back_populates="user")
    messages = relationship("ChatMessage", back_populates="user")

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String(50), unique=True, nullable=False)  # Now required for Telegram login
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