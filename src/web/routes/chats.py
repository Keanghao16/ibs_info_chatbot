from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from ..auth_decorators import any_admin_required, super_admin_required
from ...utils.apiClient import api_client

chats_bp = Blueprint('chats', __name__)

@chats_bp.route('/chats')
@any_admin_required
def chat_management():
    """Chat management - now calls API"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # 🔄 Call API for chat sessions
    response = api_client.get('/api/v1/chats', {
        'page': page,
        'per_page': per_page
    })
    
    # 🔄 Call API for chat statistics
    stats_response = api_client.get('/api/v1/chats/stats')
    
    # Handle chat sessions response
    if not response.get('success'):
        if response.get('redirect_to_login'):
            flash('Session expired. Please login again.', 'error')
            return redirect(url_for('auth.login'))
        
        flash(f"Error loading chats: {response.get('message', 'Unknown error')}", 'error')
        sessions = []
        pagination_data = {}
    else:
        sessions = response.get('data', [])
        pagination_data = response.get('pagination', {})
    
    # Handle stats response
    if not stats_response.get('success'):
        # Fallback stats if API fails - calculate from current page
        stats = {
            'total_sessions': len(sessions),
            'active_sessions': len([s for s in sessions if s.get('status') == 'active']),
            'waiting_sessions': len([s for s in sessions if s.get('status') == 'waiting']),
            'closed_sessions': len([s for s in sessions if s.get('status') == 'closed']),
            'unassigned_sessions': len([s for s in sessions if not s.get('admin_id')]),
            'total_messages': 0
        }
    else:
        stats = stats_response.get('data', {})
        # Add unassigned count to stats if not provided by API
        if 'unassigned_sessions' not in stats:
            stats['unassigned_sessions'] = len([s for s in sessions if not s.get('admin_id')])
    
    return render_template('chat/index.html', 
                         sessions=sessions, 
                         stats=stats,  # ✅ Pass stats to template
                         # Individual pagination variables
                         page=pagination_data.get('page', 1),
                         per_page=pagination_data.get('per_page', 20),
                         total=pagination_data.get('total', 0),
                         total_pages=pagination_data.get('total_pages', 1),
                         has_next=pagination_data.get('has_next', False),
                         has_prev=pagination_data.get('has_prev', False),
                         pagination=pagination_data)

@chats_bp.route('/live-chat')
@any_admin_required
def live_chat():
    """Live chat interface for real-time communication - now calls API"""
    # 🔄 Call API for active sessions
    response = api_client.get('/api/v1/chats', {
        'status': 'active',
        'per_page': 50  # Get more sessions for live chat
    })
    
    if not response.get('success'):
        if response.get('redirect_to_login'):
            flash('Session expired. Please login again.', 'error')
            return redirect(url_for('auth.login'))
        
        flash(f"Error loading active chats: {response.get('message', 'Unknown error')}", 'error')
        active_sessions = []
    else:
        active_sessions = response.get('data', [])
    
    # Get current admin info from session
    current_admin = session.get('admin', {})
    admin_role = current_admin.get('role')
    
    # Filter sessions for regular admins (only their assigned sessions)
    if admin_role == 'admin':
        admin_id = current_admin.get('id')
        active_sessions = [s for s in active_sessions if s.get('admin_id') == admin_id]
    
    return render_template('chat/live_chat.html', 
                         sessions=active_sessions,
                         admin=current_admin,
                         admin_role=admin_role)

@chats_bp.route('/chat/<int:session_id>')
@any_admin_required
def chat_detail(session_id):
    """View detailed chat session - now calls API"""
    # 🔄 Call API instead of service
    response = api_client.get(f'/api/v1/chats/{session_id}')
    
    if not response.get('success'):
        if response.get('redirect_to_login'):
            flash('Session expired. Please login again.', 'error')
            return redirect(url_for('auth.login'))
        
        flash(f"Error loading chat: {response.get('message', 'Chat not found')}", 'error')
        return redirect(url_for('chats.chat_management'))
    
    chat_session = response.get('data')
    messages = chat_session.get('messages', [])
    
    return render_template('chat/live_chat.html',
                         chat_session=chat_session,
                         messages=messages)

@chats_bp.route('/chat/send-message', methods=['POST'])
@any_admin_required
def send_message():
    """Send message to user (for admin communication) - now calls API"""
    session_id = request.form.get('session_id')
    message_text = request.form.get('message')
    current_admin_id = session['admin']['id']
    
    # 🔄 Call API instead of service
    response = api_client.post(f'/api/v1/chats/{session_id}/messages', {
        'user_id': session['admin']['id'],  # This might need adjustment based on API
        'admin_id': current_admin_id,
        'message': message_text,
        'is_from_admin': True
    })
    
    if response.get('success'):
        return jsonify(response)
    else:
        if response.get('redirect_to_login'):
            return jsonify({'success': False, 'message': 'Session expired'})
        
        return jsonify({
            'success': False, 
            'message': response.get('message', 'Error sending message')
        })

@chats_bp.route('/chat/close/<int:session_id>', methods=['POST'])
@any_admin_required
def close_chat(session_id):
    """Close a chat session - now calls API"""
    # 🔄 Call API instead of service
    response = api_client.post(f'/api/v1/chats/{session_id}/close')
    
    if response.get('success'):
        return jsonify(response)
    else:
        if response.get('redirect_to_login'):
            return jsonify({'success': False, 'message': 'Session expired'})
        
        return jsonify({
            'success': False, 
            'message': response.get('message', 'Error closing chat')
        })

@chats_bp.route('/chat/stats')
@any_admin_required
def chat_stats():
    """API endpoint for chat statistics - now calls API"""
    # 🔄 Call API instead of service
    response = api_client.get('/api/v1/chats/stats')
    
    if response.get('success'):
        return jsonify(response)
    else:
        if response.get('redirect_to_login'):
            return jsonify({'success': False, 'message': 'Session expired'})
        
        return jsonify({
            'success': False,
            'message': response.get('message', 'Error fetching statistics')
        })

@chats_bp.route('/chat/history/<user_id>')
@any_admin_required
def user_chat_history(user_id):
    """Get chat history for a specific user with pagination - now calls API"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # 🔄 Call API instead of service
    response = api_client.get('/api/v1/chats', {
        'user_id': user_id,
        'page': page,
        'per_page': per_page
    })
    
    if response.get('success'):
        return jsonify(response)
    else:
        if response.get('redirect_to_login'):
            return jsonify({'success': False, 'message': 'Session expired'})
        
        return jsonify({
            'success': False,
            'message': response.get('message', 'Error fetching chat history')
        })

@chats_bp.route('/chat/<int:session_id>/messages')
@any_admin_required
def get_chat_messages_route(session_id):
    """Get messages for a specific chat session with pagination - now calls API"""
    # 🔄 Call API instead of service
    response = api_client.get(f'/api/v1/chats/{session_id}/messages')
    
    if response.get('success'):
        return jsonify(response)
    else:
        if response.get('redirect_to_login'):
            return jsonify({'success': False, 'message': 'Session expired'})
        
        return jsonify({
            'success': False,
            'message': response.get('message', 'Error fetching messages')
        })

