# ============================================================================
# FILE: src/web/websocket_manager.py
# FIXED: Proper real-time broadcasting with Flask-SocketIO
# ============================================================================

from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request, session
import asyncio
from telegram import Bot
import os
from datetime import datetime

socketio = SocketIO(cors_allowed_origins="*")

# Store active connections: {admin_id: socket_id}
active_connections = {}

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    admin_id = session.get('admin', {}).get('id')
    if admin_id:
        room = f"admin_{admin_id}"
        join_room(room)
        active_connections[admin_id] = request.sid
        emit('connected', {'message': 'Connected to chat server'})
        print(f"✅ Admin {admin_id} connected - Socket ID: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    admin_id = session.get('admin', {}).get('id')
    if admin_id and admin_id in active_connections:
        del active_connections[admin_id]
        print(f"❌ Admin {admin_id} disconnected")

@socketio.on('send_message')
def handle_send_message(data):
    """Handle message from admin to user via Telegram"""
    try:
        from ..database.connection import SessionLocal
        from ..database.models import ChatMessage, ChatSession
        
        db = SessionLocal()
        session_id = data.get('session_id')
        message_text = data.get('message')
        admin_id = session.get('admin', {}).get('id')
        
        if not session_id:
            emit('error', {'message': 'Session ID is required'})
            db.close()
            return
        
        # Get chat session
        chat_session = db.query(ChatSession).filter(
            ChatSession.id == session_id
        ).first()
        
        if not chat_session:
            emit('error', {'message': 'Session not found'})
            db.close()
            return
        
        # Save message to database with session_id
        new_message = ChatMessage(
            session_id=session_id,
            user_id=chat_session.user_id,
            admin_id=admin_id,
            message=message_text,
            is_from_admin=True,
            timestamp=datetime.now()
        )
        db.add(new_message)
        db.commit()
        
        # Send message via Telegram
        bot_token = os.getenv('BOT_TOKEN')
        bot = Bot(token=bot_token)
        
        try:
            asyncio.run(bot.send_message(
                chat_id=chat_session.user.telegram_id,
                text=f"💬 *Agent {session.get('admin', {}).get('full_name')}:*\n\n{message_text}",
                parse_mode='Markdown'
            ))
        except Exception as e:
            print(f"❌ Error sending Telegram message: {e}")
        
        # Broadcast to admin's room (confirmation)
        emit('message_sent', {
            'id': new_message.id,
            'message': message_text,
            'timestamp': new_message.timestamp.isoformat(),
            'is_from_admin': True
        }, room=f"admin_{admin_id}")
        
        print(f"✅ Message sent from admin {admin_id} to user via Telegram")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        import traceback
        traceback.print_exc()
        emit('error', {'message': str(e)})

@socketio.on('error')
def handle_error(error):
    """Handle WebSocket errors"""
    print(f"WebSocket error: {error}")

@socketio.on_error_default
def default_error_handler(e):
    """Handle all other errors"""
    print(f"WebSocket default error: {e}")

# ============================================================================
# CRITICAL FIX: Broadcast functions for bot messages
# These should ONLY be called from within the web app context
# ============================================================================

def broadcast_new_message_internal(user_id, message_text, admin_id=None, session_id=None, user_name=None):
    """
    Internal function to broadcast messages - ONLY callable from web app context
    Do NOT call this from the API - use the /api/broadcast-message web endpoint instead
    """
    try:
        print(f"📡 Broadcasting message to admin {admin_id} for session {session_id}")
        
        # Check if socketio is properly initialized
        if not socketio.server:
            print("⚠️ SocketIO not initialized - cannot broadcast")
            return
        
        if admin_id:
            # Broadcast to specific admin's room
            socketio.emit('new_message', {
                'user_id': user_id,
                'user_name': user_name,
                'message': message_text,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'is_from_admin': False
            }, room=f"admin_{admin_id}", namespace='/')
            
            print(f"✅ Message broadcasted to admin {admin_id}")
        else:
            # Broadcast to all connected admins (for waiting sessions)
            socketio.emit('new_waiting_session', {
                'session_id': session_id,
                'user_id': user_id,
                'user_name': user_name,
                'message': message_text,
                'timestamp': datetime.now().isoformat()
            }, namespace='/')
            
            print(f"✅ New waiting session broadcasted to all admins")
            
    except Exception as e:
        print(f"❌ Error broadcasting message: {e}")
        import traceback
        traceback.print_exc()