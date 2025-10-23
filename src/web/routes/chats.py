from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from ...database.connection import SessionLocal
from ...database.models import ChatSession, User, Admin
from ...services.chat_service import ChatService
from .auth import any_admin_required

chats_bp = Blueprint('chats', __name__)
chat_service = ChatService()

@chats_bp.route('/chats')
@any_admin_required
def chat_management():
    """Chat management interface for admins to communicate with users"""
    db = SessionLocal()
    try:
        current_admin_id = session['admin_info']['id']
        
        if session['admin_info']['role'] == 'admin':
            active_sessions = chat_service.get_active_chat_sessions(db, current_admin_id)
        else:
            active_sessions = chat_service.get_active_chat_sessions(db)
            
        return render_template('chat/index.html', sessions=active_sessions)
    finally:
        db.close()

@chats_bp.route('/chat/<int:session_id>')
@any_admin_required
def chat_detail(session_id):
    """View specific chat session"""
    db = SessionLocal()
    try:
        current_admin_id = session['admin_info']['id']
        admin_role = session['admin_info']['role']
        
        # Check access
        access_result = chat_service.check_chat_access(db, session_id, current_admin_id, admin_role)
        
        if not access_result['success']:
            flash(access_result['message'], 'error')
            return redirect(url_for('chats.chat_management'))
        
        chat_session = access_result['session']
        
        # Get messages for this session
        messages = chat_service.get_chat_messages(db, chat_session.user_id)
        
        return render_template('chat/chat_detail.html', 
                             session=chat_session, 
                             messages=messages)
    finally:
        db.close()

@chats_bp.route('/chat/send-message', methods=['POST'])
@any_admin_required
def send_message():
    """Send message to user (for admin communication)"""
    db = SessionLocal()
    try:
        session_id = request.form.get('session_id')
        message_text = request.form.get('message')
        current_admin_id = session['admin_info']['id']
        admin_role = session['admin_info']['role']
        
        result = chat_service.send_chat_message(
            db=db,
            session_id=session_id,
            admin_id=current_admin_id,
            message_text=message_text,
            admin_role=admin_role
        )
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error sending message: {e}")
        return jsonify({'success': False, 'message': str(e)})
    finally:
        db.close()

@chats_bp.route('/chat/close/<int:session_id>', methods=['POST'])
@any_admin_required
def close_chat(session_id):
    """Close a chat session"""
    db = SessionLocal()
    try:
        current_admin_id = session['admin_info']['id']
        admin_role = session['admin_info']['role']
        
        result = chat_service.close_chat_session(
            db=db,
            session_id=session_id,
            admin_id=current_admin_id,
            admin_role=admin_role
        )
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error closing chat: {e}")
        return jsonify({'success': False, 'message': str(e)})
    finally:
        db.close()

@chats_bp.route('/chat/stats')
@any_admin_required
def chat_stats():
    """API endpoint for chat statistics"""
    db = SessionLocal()
    try:
        admin_id = session['admin_info']['id'] if session['admin_info']['role'] == 'admin' else None
        stats = chat_service.get_chat_statistics(db, admin_id)
        
        return jsonify({"success": True, "stats": stats})
    finally:
        db.close()

@chats_bp.route('/chat/history/<int:user_id>')
@any_admin_required
def user_chat_history(user_id):
    """Get chat history for a specific user"""
    db = SessionLocal()
    try:
        chats = chat_service.get_user_chats(db, user_id)
        
        return jsonify({
            "success": True,
            "chats": [{
                "id": chat.id,
                "start_time": chat.start_time.isoformat() if chat.start_time else None,
                "end_time": chat.end_time.isoformat() if chat.end_time else None,
                "status": chat.status.value if chat.status else None,
                "admin_id": chat.admin_id
            } for chat in chats]
        })
    finally:
        db.close()

