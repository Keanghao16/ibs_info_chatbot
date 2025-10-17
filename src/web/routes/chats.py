from flask import Blueprint, render_template
from ...database.connection import SessionLocal
from ...database.models import ChatSession, User

chats_bp = Blueprint('chats', __name__)

@chats_bp.route('/chats')
def chat_history():
    db = SessionLocal()
    try:
        chat_sessions = db.query(ChatSession).all()
        return render_template('chat_history.html', chat_sessions=chat_sessions)
    finally:
        db.close()