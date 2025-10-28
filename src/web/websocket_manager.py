from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request, session
import asyncio
from telegram import Bot
import os
from datetime import datetime, timezone  # Add timezone import

socketio = SocketIO(cors_allowed_origins="*")

# Store active connections
active_connections = {}

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    admin_id = session.get('admin_info', {}).get('id')
    if admin_id:
        room = f"admin_{admin_id}"
        join_room(room)
        active_connections[admin_id] = request.sid
        emit('connected', {'message': 'Connected to chat server'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    admin_id = session.get('admin_info', {}).get('id')
    if admin_id and admin_id in active_connections:
        del active_connections[admin_id]

@socketio.on('send_message')
def handle_send_message(data):
    """Handle message from admin to user via Telegram"""
    try:
        from ..database.connection import SessionLocal
        from ..database.models import ChatMessage, ChatSession
        
        db = SessionLocal()
        session_id = data.get('session_id')
        message_text = data.get('message')
        admin_id = session.get('admin_info', {}).get('id')
        
        # Get chat session
        chat_session = db.query(ChatSession).filter(
            ChatSession.id == session_id
        ).first()
        
        if not chat_session:
            emit('error', {'message': 'Session not found'})
            return
        
        # Save message to database with timezone-aware timestamp
        new_message = ChatMessage(
            user_id=chat_session.user_id,
            admin_id=admin_id,
            message=message_text,
            is_from_admin=True,
            timestamp=datetime.now(timezone.utc)  # ✅ Use UTC with timezone
        )
        db.add(new_message)
        db.commit()
        
        # Send message via Telegram
        bot_token = os.getenv('BOT_TOKEN')
        bot = Bot(token=bot_token)
        
        asyncio.run(bot.send_message(
            chat_id=chat_session.user.telegram_id,
            text=f"💬 *Agent {session.get('admin_info', {}).get('full_name')}:*\n\n{message_text}",
            parse_mode='Markdown'
        ))
        
        # Broadcast to admin's room
        emit('message_sent', {
            'id': new_message.id,
            'message': message_text,
            'timestamp': new_message.timestamp.isoformat(),
            'is_from_admin': True
        }, room=f"admin_{admin_id}")
        
        db.close()
        
    except Exception as e:
        print(f"Error sending message: {e}")
        emit('error', {'message': str(e)})

@socketio.on('error')
def handle_error(error):
    """Handle WebSocket errors"""
    print(f"WebSocket error: {error}")
    emit('error', {'message': 'Connection error occurred'})

@socketio.on_error_default
def default_error_handler(e):
    """Default error handler"""
    print(f"WebSocket error: {e}")

def broadcast_new_message(user_id, message_text, admin_id=None, session_id=None):
    """Broadcast new message from user to admin"""
    if admin_id and admin_id in active_connections:
        socketio.emit('new_message', {
            'user_id': user_id,
            'session_id': session_id,
            'message': message_text,
            'timestamp': datetime.now(timezone.utc).isoformat()  # ✅ Add timezone.utc
        }, room=f"admin_{admin_id}")