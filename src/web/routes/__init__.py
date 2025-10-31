# filepath: telegram-chatbot-admin/src/web/routes/__init__.py
from flask import Blueprint

routes = Blueprint('routes', __name__)

# Import all route modules
from . import admin, users, chats, auth, dashboard, system_settings

# Export blueprints for easy import
from .auth import auth_bp
from .admin import admin_bp
from .users import users_bp
from .chats import chats_bp
from .dashboard import dashboard_bp
from .system_settings import system_settings_bp

__all__ = [
    'auth_bp',
    'admin_bp', 
    'users_bp',
    'chats_bp',
    'dashboard_bp',
    'system_settings_bp'
]