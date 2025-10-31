from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from ...database.connection import SessionLocal
from ...database.models import ChatSession, User, Admin
from ...services import ChatService
from .auth import any_admin_required
from ...utils import Helpers

chats_bp = Blueprint('chats', __name__)
chat_service = ChatService()

@chats_bp.route('/chats')
@any_admin_required
def chat_management():
    """Chat management interface for admins to communicate with users"""
    db = SessionLocal()
    try:
        current_admin_id = session['admin_info']['id']
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 15, type=int)
        
        if session['admin_info']['role'] == 'admin':
            active_sessions = chat_service.get_active_chat_sessions(db, current_admin_id)
        else:
            active_sessions = chat_service.get_active_chat_sessions(db)
        
        # Apply pagination
        paginated_sessions = Helpers.paginate(active_sessions, page, per_page)
        
        # Calculate total pages
        total_sessions = len(active_sessions)
        total_pages = (total_sessions + per_page - 1) // per_page
        
        return render_template('chat/index.html', 
                             sessions=paginated_sessions,
                             page=page,
                             per_page=per_page,
                             total_sessions=total_sessions,
                             total_pages=total_pages)
    finally:
        db.close()

@chats_bp.route('/live-chat')
@any_admin_required
def live_chat():
    """Live chat interface for real-time communication"""
    db = SessionLocal()
    try:
        current_admin_id = session['admin_info']['id']
        admin_role = session['admin_info']['role']
        
        # Get active sessions based on admin role
        if admin_role == 'admin':
            active_sessions = chat_service.get_active_chat_sessions(db, current_admin_id)
        else:
            active_sessions = chat_service.get_active_chat_sessions(db)
        
        # Get admin info
        admin = db.query(Admin).filter(Admin.id == current_admin_id).first()
        
        return render_template('chat/live_chat.html', 
                             sessions=active_sessions,
                             admin=admin,
                             admin_role=admin_role)
    finally:
        db.close()

@chats_bp.route('/chat/<int:session_id>')
@any_admin_required
def chat_detail(session_id):
    """View detailed chat session"""
    db = SessionLocal()
    try:
        current_admin_id = session['admin_info']['id']
        admin_role = session['admin_info']['role']
        
        # Check access
        access_result = chat_service.check_chat_access(db, session_id, current_admin_id, admin_role)
        
        if not access_result['success']:
            flash(access_result['message'], 'error')
            return redirect(url_for('chats.chat_management'))
        
        # Get chat session
        chat_session = chat_service.get_chat_by_id(db, session_id)
        
        if not chat_session:
            flash('Chat session not found', 'error')
            return redirect(url_for('chats.chat_management'))
        
        # Get messages
        messages = chat_service.get_session_messages(db, session_id)
        
        return render_template('chat/detail.html',
                             chat_session=chat_session,
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
    """Get chat history for a specific user with pagination"""
    db = SessionLocal()
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        chats = chat_service.get_user_chats(db, user_id)
        
        # Apply pagination
        paginated_chats = Helpers.paginate(chats, page, per_page)
        
        return jsonify({
            "success": True,
            "chats": [{
                "id": chat.id,
                "start_time": Helpers.format_timestamp(chat.start_time) if chat.start_time else None,
                "end_time": Helpers.format_timestamp(chat.end_time) if chat.end_time else None,
                "status": chat.status.value if chat.status else None,
                "admin_id": chat.admin_id
            } for chat in paginated_chats],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": len(chats),
                "total_pages": (len(chats) + per_page - 1) // per_page
            }
        })
    finally:
        db.close()

@chats_bp.route('/api/chats')
@any_admin_required
def get_chats():
    """Get all chats with formatted timestamps and pagination"""
    db = SessionLocal()
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        chats = chat_service.get_all_chats()
        
        # Apply pagination
        paginated_chats = Helpers.paginate(chats, page, per_page)
        
        return jsonify({
            'success': True,
            'chats': paginated_chats,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': len(chats),
                'total_pages': (len(chats) + per_page - 1) // per_page
            }
        })
    finally:
        db.close()

@chats_bp.route('/chat/<int:session_id>/messages')
@any_admin_required
def get_chat_messages_route(session_id):
    """Get messages for a specific chat session with pagination"""
    db = SessionLocal()
    try:
        current_admin_id = session['admin_info']['id']
        admin_role = session['admin_info']['role']
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        # Check access
        access_result = chat_service.check_chat_access(db, session_id, current_admin_id, admin_role)
        
        if not access_result['success']:
            return jsonify({'success': False, 'message': access_result['message']})
        
        # Get messages for this specific session
        messages = chat_service.get_session_messages(db, session_id)
        
        # Apply pagination
        paginated_messages = Helpers.paginate(messages, page, per_page)
        
        return jsonify({
            'success': True,
            'messages': [{
                'id': msg.id,
                'message': msg.message,
                'is_from_admin': msg.is_from_admin,
                'timestamp': Helpers.format_timestamp(msg.timestamp) if msg.timestamp else None,
                'admin_name': msg.admin.full_name if msg.admin else None
            } for msg in paginated_messages],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': len(messages),
                'total_pages': (len(messages) + per_page - 1) // per_page
            }
        })
    except Exception as e:
        print(f"❌ Error getting messages: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)})
    finally:
        db.close()

