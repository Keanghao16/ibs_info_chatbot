# ============================================================================
# FILE: src/web/routes/chats.py
# UPDATED: Show waiting sessions in live chat
# ============================================================================

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from ..auth_decorators import any_admin_required, super_admin_required
from ...utils.apiClient import api_client

chats_bp = Blueprint('chats', __name__)

@chats_bp.route('/api/active-chats-count')
@any_admin_required
def get_active_chats_count():
    """Get count of waiting (unassigned) chats for badge display"""
    try:
        # Call API for chat statistics
        stats_response = api_client.get('/api/v1/chats/stats')
        
        if stats_response.get('success'):
            stats = stats_response.get('data', {})
            # Only count WAITING sessions (unassigned) for the badge
            waiting_count = stats.get('waiting_sessions', 0)
            active_count = stats.get('active_sessions', 0)
            
            return jsonify({
                'success': True,
                'count': waiting_count,  # Badge shows only waiting/unassigned
                'details': {
                    'active': active_count,
                    'waiting': waiting_count,
                    'total': active_count + waiting_count
                }
            })
        else:
            return jsonify({
                'success': False,
                'count': 0
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'count': 0,
            'error': str(e)
        })

@chats_bp.route('/api/chat-session/<int:session_id>')
@any_admin_required
def get_chat_session(session_id):
    """Get a single chat session by ID"""
    try:
        response = api_client.get(f'/api/v1/chats/{session_id}')
        
        if response.get('success'):
            return jsonify({
                'success': True,
                'session': response.get('data')
            })
        else:
            return jsonify({
                'success': False,
                'message': response.get('message', 'Session not found')
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@chats_bp.route('/api/broadcast-message', methods=['POST'])
def broadcast_message_endpoint():
    """Endpoint for API server to trigger Socket.IO broadcast"""
    try:
        from ..websocket_manager import broadcast_new_message_internal
        
        data = request.json
        required_fields = ['session_id', 'user_id', 'message']
        
        if not all(field in data for field in required_fields):
            return jsonify({
                'success': False,
                'message': 'Missing required fields'
            }), 400
        
        # Trigger Socket.IO broadcast
        broadcast_new_message_internal(
            user_id=data['user_id'],
            message_text=data['message'],
            admin_id=data.get('admin_id'),
            session_id=data['session_id'],
            user_name=data.get('user_name')
        )
        
        print(f"✅ Socket.IO broadcast triggered for session {data['session_id']}")
        
        return jsonify({
            'success': True,
            'message': 'Message broadcasted successfully'
        })
                
    except Exception as e:
        print(f"❌ Error broadcasting message: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@chats_bp.route('/api/broadcast-new-session', methods=['POST'])
def broadcast_new_session_endpoint():
    """Endpoint for API server to trigger Socket.IO broadcast for new session"""
    try:
        from ..websocket_manager import broadcast_new_session
        
        data = request.json
        required_fields = ['session_id', 'user_id']
        
        if not all(field in data for field in required_fields):
            return jsonify({
                'success': False,
                'message': 'Missing required fields'
            }), 400
        
        # Trigger Socket.IO broadcast
        broadcast_new_session(
            session_id=data['session_id'],
            user_id=data['user_id'],
            user_name=data.get('user_name')
        )
        
        print(f"✅ Socket.IO new session broadcast triggered for session {data['session_id']}")
        
        return jsonify({
            'success': True,
            'message': 'New session broadcasted successfully'
        })
                
    except Exception as e:
        print(f"❌ Error broadcasting new session: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@chats_bp.route('/api/chats')
@any_admin_required
def get_filtered_chats():
    """API endpoint to get filtered chat sessions"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', None)  # 'waiting', 'active', 'closed', or None for all
    
    # Build API params
    params = {
        'page': page,
        'per_page': per_page
    }
    
    if status:
        params['status'] = status
    
    # 🔄 Call API for filtered chat sessions
    response = api_client.get('/api/v1/chats', params)
    
    if not response.get('success'):
        if response.get('redirect_to_login'):
            return jsonify({'success': False, 'message': 'Session expired'}), 401
        
        return jsonify({'success': False, 'message': response.get('message', 'Failed to fetch sessions')}), 400
    
    return jsonify({
        'success': True,
        'data': response.get('data', {}),
        'pagination': response.get('pagination', {})
    })

@chats_bp.route('/chats')
@any_admin_required
def chat_management():
    """Chat management - now calls API"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', None)  # Get status filter from query params
    
    # Build API params
    params = {
        'page': page,
        'per_page': per_page
    }
    
    if status:
        params['status'] = status
    
    # 🔄 Call API for chat sessions
    response = api_client.get('/api/v1/chats', params)
    
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
                         stats=stats,
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
    # Get session_id from URL parameter if provided
    session_id_param = request.args.get('session_id')
    
    # 🔄 UPDATED: Get both waiting AND active sessions
    response = api_client.get('/api/v1/chats', {
        'per_page': 100  # Get more sessions for live chat
    })
    
    if not response.get('success'):
        if response.get('redirect_to_login'):
            flash('Session expired. Please login again.', 'error')
            return redirect(url_for('auth.login'))
        
        flash(f"Error loading chats: {response.get('message', 'Unknown error')}", 'error')
        sessions = []
    else:
        all_sessions = response.get('data', [])
        # 🆕 Filter to only show waiting and active sessions (not closed)
        sessions = [s for s in all_sessions if s.get('status') in ['waiting', 'active']]
    
    # Get current admin info from session
    current_admin = session.get('admin', {})
    admin_role = current_admin.get('role')
    admin_id = current_admin.get('id')
    
    # Filter sessions for regular admins (only their assigned sessions + unassigned waiting)
    if admin_role == 'admin':
        sessions = [
            s for s in sessions 
            if s.get('admin_id') == admin_id or  # Their assigned sessions
               (s.get('status') == 'waiting' and not s.get('admin_id'))  # Unassigned waiting sessions
        ]
    
    return render_template('chat/live_chat.html', 
                         sessions=sessions,
                         admin=current_admin,
                         admin_role=admin_role,
                         preselect_session_id=session_id_param)


@chats_bp.route('/chat/<int:session_id>')
@any_admin_required
def chat_detail(session_id):
    """Get detailed chat session - now calls API"""
    # 🔄 Call API for session details
    response = api_client.get(f'/api/v1/chats/{session_id}')
    
    if not response.get('success'):
        if response.get('redirect_to_login'):
            flash('Session expired. Please login again.', 'error')
            return redirect(url_for('auth.login'))
        
        flash(f"Chat session not found: {response.get('message', 'Unknown error')}", 'error')
        return redirect(url_for('chats.chat_management'))
    
    chat_session = response.get('data')
    
    return render_template('chat/live_chat.html', session=chat_session)


@chats_bp.route('/chat/send-message', methods=['POST'])
@any_admin_required
def send_message():
    """Send message via API"""
    session_id = request.form.get('session_id')
    message = request.form.get('message')
    
    # 🔄 Call API to send message
    response = api_client.post(f'/api/v1/chats/{session_id}/messages', {
        'message': message,
        'admin_id': session.get('admin', {}).get('id')
    })
    
    if not response.get('success'):
        if response.get('redirect_to_login'):
            return jsonify({'success': False, 'message': 'Session expired'}), 401
        
        return jsonify({'success': False, 'message': response.get('message', 'Failed to send message')}), 400
    
    return jsonify({'success': True, 'message': 'Message sent successfully'})


# 🆕 ADD THIS NEW ROUTE for assigning sessions
@chats_bp.route('/chat/assign/<int:session_id>', methods=['POST'])
@any_admin_required
def assign_session(session_id):
    """Assign session to current admin"""
    admin_id = session.get('admin', {}).get('id')
    
    # 🔄 Call API to assign session
    response = api_client.put(f'/api/v1/chats/{session_id}/assign', {
        'admin_id': admin_id
    })
    
    if not response.get('success'):
        if response.get('redirect_to_login'):
            return jsonify({'success': False, 'message': 'Session expired'}), 401
        
        return jsonify({'success': False, 'message': response.get('message', 'Failed to assign session')}), 400
    
    # Broadcast session assignment to all admins
    try:
        from ..websocket_manager import broadcast_session_assigned
        session_data = response.get('data', {})
        user_name = None
        if session_data and 'user' in session_data:
            user_name = session_data['user'].get('full_name')
        
        print(f"🔔 Broadcasting session {session_id} assignment to admin {admin_id}, user: {user_name}")
        broadcast_session_assigned(
            session_id=session_id,
            admin_id=admin_id,
            user_name=user_name
        )
        print(f"✅ Broadcast completed for session assignment")
    except Exception as e:
        print(f"⚠️ Failed to broadcast session assignment: {e}")
        import traceback
        traceback.print_exc()
    
    return jsonify({'success': True, 'message': 'Session assigned successfully', 'data': response.get('data')})


@chats_bp.route('/chat/close/<int:session_id>', methods=['POST'])
@any_admin_required
def close_chat(session_id):
    """Close chat session via API"""
    # 🔄 Call API to close session
    response = api_client.post(f'/api/v1/chats/{session_id}/close', {})
    
    if not response.get('success'):
        return jsonify({
            'success': False,
            'message': response.get('message', 'Failed to close chat session')
        }), 400
    
    # Broadcast session closed to all admins
    try:
        from ..websocket_manager import broadcast_session_closed
        broadcast_session_closed(session_id)
    except Exception as e:
        print(f"⚠️ Failed to broadcast session closed: {e}")
    
    return jsonify({
        'success': True,
        'message': 'Chat session closed successfully'
    })


@chats_bp.route('/chat/stats')
@any_admin_required
def chat_stats():
    """Get chat statistics via API"""
    # 🔄 Call API for stats
    response = api_client.get('/api/v1/chats/stats')
    
    if not response.get('success'):
        if response.get('redirect_to_login'):
            return jsonify({'success': False, 'message': 'Session expired'}), 401
        
        return jsonify({'success': False, 'message': response.get('message', 'Failed to get stats')}), 400
    
    return jsonify({'success': True, 'data': response.get('data')})


@chats_bp.route('/chat/history/<user_id>')
@any_admin_required
def user_chat_history(user_id):
    """Get user's chat history via API"""
    # 🔄 Call API for user's sessions
    response = api_client.get('/api/v1/chats', {
        'user_id': user_id,
        'per_page': 50
    })
    
    if not response.get('success'):
        if response.get('redirect_to_login'):
            flash('Session expired. Please login again.', 'error')
            return redirect(url_for('auth.login'))
        
        flash(f"Failed to load chat history: {response.get('message', 'Unknown error')}", 'error')
        sessions = []
    else:
        sessions = response.get('data', [])
    
    return render_template('chat/history.html', sessions=sessions, user_id=user_id)


@chats_bp.route('/chat/<int:session_id>/messages')
@any_admin_required
def get_chat_messages_route(session_id):
    """Get messages for a specific session via API"""
    # 🔄 Call API for session messages
    response = api_client.get(f'/api/v1/chats/{session_id}/messages')
    
    if not response.get('success'):
        if response.get('redirect_to_login'):
            return jsonify({'success': False, 'message': 'Session expired'}), 401
        
        return jsonify({'success': False, 'message': response.get('message', 'Failed to load messages')}), 400
    
    return jsonify({'success': True, 'data': response.get('data', [])})


# Add this new route at the end of the file

@chats_bp.route('/api/broadcast-message', methods=['POST'])
def broadcast_message():
    """
    Internal endpoint for broadcasting messages via WebSocket
    Called by the API to trigger real-time updates
    """
    try:
        from ..websocket_manager import broadcast_new_message_internal
        
        data = request.json
        
        # Broadcast the message
        broadcast_new_message_internal(
            user_id=data.get('user_id'),
            message_text=data.get('message'),
            admin_id=data.get('admin_id'),
            session_id=data.get('session_id'),
            user_name=data.get('user_name')
        )
        
        return jsonify({
            'success': True,
            'message': 'Message broadcasted'
        })
        
    except Exception as e:
        print(f"❌ Error in broadcast endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# Add this route at the end of the file

@chats_bp.route('/api/session-counts', methods=['GET'])
@any_admin_required
def get_session_counts():
    """Get counts of waiting and active sessions for notification badges"""
    try:
        # Get current admin if they're a regular admin (not super_admin)
        current_admin = session.get('admin', {})
        admin_id = current_admin.get('id')
        is_super_admin = current_admin.get('role') == 'super_admin'
        
        # Build query parameters
        params = {}
        
        # Regular admins only see their assigned sessions
        if not is_super_admin and admin_id:
            params['admin_id'] = admin_id
        
        # Get waiting sessions count
        waiting_params = {**params, 'status': 'waiting', 'per_page': 1}
        waiting_response = api_client.get('/api/v1/chats', waiting_params)
        waiting_count = waiting_response.get('data', {}).get('pagination', {}).get('total', 0) if waiting_response.get('success') else 0
        
        # Get active sessions count
        active_params = {**params, 'status': 'active', 'per_page': 1}
        active_response = api_client.get('/api/v1/chats', active_params)
        active_count = active_response.get('data', {}).get('pagination', {}).get('total', 0) if active_response.get('success') else 0
        
        return jsonify({
            'success': True,
            'waiting_count': waiting_count,
            'active_count': active_count,
            'total_count': waiting_count + active_count
        })
        
    except Exception as e:
        print(f"❌ Error getting session counts: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

