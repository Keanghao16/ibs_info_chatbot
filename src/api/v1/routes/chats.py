"""
Chats API Routes
Handles all chat-related API endpoints
"""

from flask import Blueprint, request, jsonify
from ..middleware.auth import token_required, admin_required
from ..schemas import (
    ChatSessionResponseSchema,
    ChatSessionListResponseSchema,
    ChatSessionCreateSchema,
    ChatSessionUpdateSchema,
    MessageCreateSchema,
    ChatMessageResponseSchema,
    ChatAssignSchema,
    ChatStatsSchema,
    success_response,
    error_response,
    paginated_response,
    created_response,
    updated_response,
    not_found_response,
    validation_error_response
)
from ....services.chat_service import ChatService
from ....database.connection import get_db_session
from marshmallow import ValidationError
import traceback

# Create blueprint
chats_api_bp = Blueprint('chats_api', __name__)

# Initialize schemas
session_response_schema = ChatSessionResponseSchema()
session_list_schema = ChatSessionListResponseSchema(many=True)
session_create_schema = ChatSessionCreateSchema()
session_update_schema = ChatSessionUpdateSchema()
message_create_schema = MessageCreateSchema()
message_response_schema = ChatMessageResponseSchema()
message_list_schema = ChatMessageResponseSchema(many=True)
chat_assign_schema = ChatAssignSchema()
chat_stats_schema = ChatStatsSchema()


@chats_api_bp.route('/chats', methods=['GET'])
@token_required
@admin_required
def list_chat_sessions(current_user):
    """
    Get paginated list of chat sessions
    
    Query Parameters:
        - page (int): Page number
        - per_page (int): Items per page
        - status (str): Filter by status (waiting/active/closed)
        - admin_id (str): Filter by assigned admin (UUID)
        - user_id (str): Filter by user (UUID)
    """
    db = get_db_session()
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        status = request.args.get('status')
        admin_id = request.args.get('admin_id')  #  String (UUID)
        user_id = request.args.get('user_id')  #  String (UUID)
        
        result = ChatService.get_all_sessions(
            db=db,
            page=page,
            per_page=per_page,
            status=status,
            admin_id=admin_id,
            user_id=user_id
        )
        
        #  Serialize sessions with proper data
        sessions_data = []
        for session in result['sessions']:
            session_dict = {
                'id': session.id,
                'user_id': session.user_id,
                'admin_id': session.admin_id,
                'status': session.status.value if hasattr(session.status, 'value') else session.status,
                'start_time': session.start_time.isoformat() if session.start_time else None,
                'end_time': session.end_time.isoformat() if session.end_time else None,
                'message_count': 0,  # TODO: Calculate actual count
                'user_name': session.user.full_name if session.user else None,
                'admin_name': session.admin.full_name if session.admin else None
            }
            sessions_data.append(session_dict)
        
        return paginated_response(
            data=sessions_data,
            page=result['page'],
            per_page=result['per_page'],
            total=result['total'],
            message=f"Retrieved {len(sessions_data)} chat sessions"
        )
        
    except Exception as e:
        print(f"❌ Error listing sessions: {str(e)}")
        traceback.print_exc()
        return error_response(str(e), 500)
    finally:
        db.close()


@chats_api_bp.route('/chats/<int:session_id>', methods=['GET'])
@token_required
@admin_required
def get_chat_session(current_user, session_id):
    """Get chat session with all messages"""
    db = get_db_session()
    try:
        print(f"🔍 Looking for session_id: {session_id}")
        
        session = ChatService.get_session_by_id(db, session_id)
        
        if not session:
            print(f"❌ Session {session_id} not found in database")
            return not_found_response('Chat session')
        
        #  Get messages for this session
        messages = ChatService.get_session_messages(db, session_id)
        
        #  Serialize with messages included
        session_data = {
            'id': session.id,
            'user_id': session.user_id,
            'admin_id': session.admin_id,
            'status': session.status.value if hasattr(session.status, 'value') else session.status,
            'start_time': session.start_time.isoformat() if session.start_time else None,
            'end_time': session.end_time.isoformat() if session.end_time else None,
            'user': {
                'id': session.user.id,
                'full_name': session.user.full_name,
                'telegram_id': session.user.telegram_id
            } if session.user else None,
            'admin': {
                'id': session.admin.id,
                'full_name': session.admin.full_name,
                'telegram_id': session.admin.telegram_id
            } if session.admin else None,
            'messages': [{
                'id': msg.id,
                'message': msg.message,
                'is_from_admin': msg.is_from_admin,
                'timestamp': msg.timestamp.isoformat() if msg.timestamp else None
            } for msg in messages]
        }
        
        return success_response(
            data=session_data,
            message="Chat session retrieved successfully"
        )
        
    except Exception as e:
        print(f"❌ Error getting chat session: {str(e)}")
        traceback.print_exc()
        return error_response(str(e), 500)
    finally:
        db.close()


@chats_api_bp.route('/chats', methods=['POST'])
@token_required
@admin_required
def create_chat_session(current_user):
    """
    Create new chat session
    
    Request Body:
        {
            "user_id": "dbbf2def-88bd-4ba6-9f8f-fc185b077290",  // UUID string
            "status": "waiting"
        }
    """
    db = get_db_session()
    try:
        try:
            session_data = session_create_schema.load(request.json)
        except ValidationError as err:
            return validation_error_response(err.messages)
        
        print(f"📝 Creating session with data: {session_data}")
        
        new_session = ChatService.create_session(db, session_data)
        
        session_response = {
            'id': new_session.id,
            'user_id': new_session.user_id,
            'admin_id': new_session.admin_id,
            'status': new_session.status.value if hasattr(new_session.status, 'value') else new_session.status,
            'start_time': new_session.start_time.isoformat() if new_session.start_time else None,
            'end_time': new_session.end_time.isoformat() if new_session.end_time else None
        }
        
        return created_response(
            data=session_response,
            message="Chat session created successfully"
        )
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating session: {str(e)}")
        traceback.print_exc()
        return error_response(str(e), 500)
    finally:
        db.close()


@chats_api_bp.route('/chats/<int:session_id>/assign', methods=['PUT'])
@token_required
@admin_required
def assign_chat_to_admin(current_user, session_id):
    """
    Assign chat session to admin
    
    Request Body:
        {
            "admin_id": "fa6649fd-7acd-43f5-a469-d774b01d2cc0"  // UUID string
        }
    """
    db = get_db_session()
    try:
        session = ChatService.get_session_by_id(db, session_id)
        if not session:
            return not_found_response('Chat session')
        
        try:
            assign_data = chat_assign_schema.load(request.json)
        except ValidationError as err:
            return validation_error_response(err.messages)
        
        updated_session = ChatService.assign_to_admin(
            db,
            session_id,
            assign_data['admin_id']
        )
        
        session_response = {
            'id': updated_session.id,
            'user_id': updated_session.user_id,
            'admin_id': updated_session.admin_id,
            'status': updated_session.status.value if hasattr(updated_session.status, 'value') else updated_session.status
        }
        
        return updated_response(
            data=session_response,
            message="Chat assigned to admin successfully"
        )
        
    except Exception as e:
        db.rollback()
        return error_response(str(e), 500)
    finally:
        db.close()


@chats_api_bp.route('/chats/<int:session_id>/close', methods=['POST'])
@token_required
@admin_required
def close_chat_session(current_user, session_id):
    """Close chat session"""
    db = get_db_session()
    try:
        session = ChatService.get_session_by_id(db, session_id)
        if not session:
            return not_found_response('Chat session')
        
        closed_session = ChatService.close_session(db, session_id)
        
        return updated_response(
            data={
                'id': closed_session.id,
                'status': closed_session.status.value if hasattr(closed_session.status, 'value') else closed_session.status,
                'end_time': closed_session.end_time.isoformat() if closed_session.end_time else None
            },
            message="Chat session closed successfully"
        )
        
    except Exception as e:
        db.rollback()
        return error_response(str(e), 500)
    finally:
        db.close()


@chats_api_bp.route('/chats/<int:session_id>/messages', methods=['GET'])
@token_required
@admin_required
def get_chat_messages(current_user, session_id):
    """Get all messages from a chat session"""
    db = get_db_session()
    try:
        session = ChatService.get_session_by_id(db, session_id)
        if not session:
            return not_found_response('Chat session')
        
        messages = ChatService.get_session_messages(db, session_id)
        
        messages_data = [{
            'id': msg.id,
            'session_id': session_id,
            'user_id': msg.user_id,
            'admin_id': msg.admin_id,
            'admin_name': msg.admin.full_name if msg.admin else None,
            'message': msg.message,
            'timestamp': msg.timestamp.isoformat() if msg.timestamp else None,
            'is_from_admin': msg.is_from_admin
        } for msg in messages]
        
        return success_response(
            data=messages_data,
            message=f"Retrieved {len(messages_data)} messages"
        )
        
    except Exception as e:
        return error_response(str(e), 500)
    finally:
        db.close()


@chats_api_bp.route('/chats/<int:session_id>/messages', methods=['POST'])
@token_required
@admin_required
def send_message(current_user, session_id):
    """
    Send message in chat session
    
    Request Body:
        {
            "user_id": "uuid",
            "admin_id": "uuid",  // optional
            "message": "Hello, how can I help you?",
            "is_from_admin": true
        }
    """
    db = get_db_session()
    try:
        session = ChatService.get_session_by_id(db, session_id)
        if not session:
            return not_found_response('Chat session')
        
        # Validate message data
        try:
            message_data = message_create_schema.load(request.json)
            message_data['session_id'] = session_id  # Add session_id
        except ValidationError as err:
            return validation_error_response(err.messages)
        
        new_message = ChatService.create_message(db, message_data)
        
        message_response = {
            'id': new_message.id,
            'session_id': new_message.session_id,
            'message': new_message.message,
            'is_from_admin': new_message.is_from_admin,
            'timestamp': new_message.timestamp.isoformat() if new_message.timestamp else None
        }
        
        return created_response(
            data=message_response,
            message="Message sent successfully"
        )
        
    except Exception as e:
        db.rollback()
        return error_response(str(e), 500)
    finally:
        db.close()


@chats_api_bp.route('/chats/stats', methods=['GET'])
@token_required
@admin_required
def get_chat_stats(current_user):
    """Get chat statistics"""
    db = get_db_session()
    try:
        stats = ChatService.get_chat_statistics(db)
        stats_data = chat_stats_schema.dump(stats)
        
        return success_response(
            data=stats_data,
            message="Chat statistics retrieved successfully"
        )
        
    except Exception as e:
        return error_response(str(e), 500)
    finally:
        db.close()