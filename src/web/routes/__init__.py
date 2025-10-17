# filepath: telegram-chatbot-admin/src/web/routes/__init__.py
from flask import Blueprint

routes = Blueprint('routes', __name__)

from . import admin, users, chats