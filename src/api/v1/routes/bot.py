"""
Bot API Routes
Special endpoints for Telegram Bot operations
"""
from flask import Blueprint, request, jsonify
from ..schemas import success_response, error_response, created_response, AdminResponseSchema
from ....services import UserService, FAQService, ChatService, SystemSettingService
from ....database.connection import get_db_session
from marshmallow import ValidationError
import traceback

bot_api_bp = Blueprint('bot_api', __name__)

# Initialize schema
admin_response_schema = AdminResponseSchema()

@bot_api_bp.route('/bot/user/create-or-get', methods=['POST'])
def create_or_get_user():
    """Create user or get existing (bot-specific)"""
    try:
        data = request.json
        required_fields = ['telegram_id', 'first_name']
        
        if not all(field in data for field in required_fields):
            return error_response('Missing required fields', 400)
        
        with get_db_session() as db:
            user_service = UserService()
            
            # Check if admin
            result = user_service.get_user_or_admin_by_telegram_id(db, str(data['telegram_id']))
            
            if result and result['type'] == 'admin':
                # Serialize the Admin object using schema
                admin_data = admin_response_schema.dump(result['data'])
                return success_response(
                    message='User is an admin',
                    data={'is_admin': True, 'admin': admin_data}
                )
            
            # Create or get user
            create_result = user_service.create_user_if_not_admin(
                db=db,
                telegram_id=str(data['telegram_id']),
                username=data.get('username'),
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
                full_name=data.get('full_name'),
                photo_url=data.get('photo_url')
            )
            
            if create_result['success']:
                user = create_result['user']
                return success_response(
                    message='User created or retrieved',
                    data={
                        'is_admin': False,
                        'user': {
                            'id': str(user.id),
                            'telegram_id': user.telegram_id,
                            'username': user.username,
                            'full_name': user.full_name
                        }
                    }
                )
            else:
                return error_response(create_result['message'], 400)
                
    except Exception as e:
        print(f"❌ Error in create_or_get_user: {str(e)}")
        traceback.print_exc()
        return error_response(str(e), 500)

@bot_api_bp.route('/bot/chat/create-session', methods=['POST'])
def create_chat_session():
    """Create new chat session with available admin"""
    try:
        data = request.json
        required_fields = ['user_id']
        
        if not all(field in data for field in required_fields):
            return error_response('Missing required fields', 400)
        
        with get_db_session() as db:
            chat_service = ChatService()
            
            # Create new session
            session = chat_service.create_session(db, {
                'user_id': data['user_id'],
                'status': 'waiting'
            })
            
            if session:
                return created_response(
                    message='Chat session created',
                    data={
                        'session_id': session.id,
                        'status': session.status.value,
                        'created_at': session.created_at.isoformat()
                    }
                )
            else:
                return error_response('Failed to create session', 500)
                
    except Exception as e:
        print(f"❌ Error in create_chat_session: {str(e)}")
        traceback.print_exc()
        return error_response(str(e), 500)

@bot_api_bp.route('/bot/chat/send-message', methods=['POST'])
def send_message():
    """Send message in chat session"""
    try:
        data = request.json
        required_fields = ['session_id', 'message', 'sender_type']
        
        if not all(field in data for field in required_fields):
            return error_response('Missing required fields', 400)
        
        with get_db_session() as db:
            chat_service = ChatService()
            
            # Add message to session
            message = chat_service.add_message(
                db=db,
                session_id=data['session_id'],
                sender_type=data['sender_type'],
                message_text=data['message']
            )
            
            if message:
                return success_response(
                    message='Message sent',
                    data={
                        'message_id': message.id,
                        'created_at': message.created_at.isoformat()
                    }
                )
            else:
                return error_response('Failed to send message', 500)
                
    except Exception as e:
        print(f"❌ Error in send_message: {str(e)}")
        traceback.print_exc()
        return error_response(str(e), 500)

@bot_api_bp.route('/bot/faq/categories', methods=['GET'])
def get_faq_categories():
    """Get all active FAQ categories"""
    try:
        with get_db_session() as db:
            # Use SystemSettingService instead of FAQService
            setting_service = SystemSettingService()
            categories = setting_service.get_active_categories(db)
            
            return success_response(
                message='Categories retrieved',
                data=[{
                    'id': cat.id,
                    'name': cat.name,
                    'slug': cat.slug,
                    'description': cat.description,
                    'icon': cat.icon,
                    'faq_count': setting_service.get_category_faq_count(db, cat.id)
                } for cat in categories]
            )
                
    except Exception as e:
        print(f"❌ Error in get_faq_categories: {str(e)}")
        traceback.print_exc()
        return error_response(str(e), 500)

@bot_api_bp.route('/bot/faq/category/<int:category_id>', methods=['GET'])
def get_category_faqs(category_id):
    """Get FAQs for a specific category"""
    try:
        with get_db_session() as db:
            # Use SystemSettingService instead of FAQService
            setting_service = SystemSettingService()
            
            # Check if category exists
            category = setting_service.get_category_by_id(db, category_id)
            if not category:
                return error_response('Category not found', 404)
            
            # Get FAQs for this category (active only)
            faqs = setting_service.get_faqs_by_category(db, category_id, active_only=True)
            
            return success_response(
                message='FAQs retrieved',
                data={
                    'category': {
                        'id': category.id,
                        'name': category.name,
                        'slug': category.slug,
                        'description': category.description,
                        'icon': category.icon
                    },
                    'faqs': [{
                        'id': faq.id,
                        'question': faq.question,
                        'answer': faq.answer,
                        'category_id': faq.category_id
                    } for faq in faqs]
                }
            )
                
    except Exception as e:
        print(f"❌ Error in get_category_faqs: {str(e)}")
        traceback.print_exc()
        return error_response(str(e), 500)

@bot_api_bp.route('/bot/faq/<int:faq_id>', methods=['GET'])
def get_faq_by_id(faq_id):
    """Get a specific FAQ by ID"""
    try:
        with get_db_session() as db:
            setting_service = SystemSettingService()
            
            # Get FAQ
            faq = setting_service.get_faq_by_id(db, faq_id)
            if not faq:
                return error_response('FAQ not found', 404)
            
            return success_response(
                message='FAQ retrieved',
                data={
                    'id': faq.id,
                    'question': faq.question,
                    'answer': faq.answer,
                    'category_id': faq.category_id,
                    'category_name': faq.faq_category.name if faq.faq_category else None
                }
            )
                
    except Exception as e:
        print(f"❌ Error in get_faq_by_id: {str(e)}")
        traceback.print_exc()
        return error_response(str(e), 500)

@bot_api_bp.route('/bot/faq/search', methods=['GET'])
def search_faqs():
    """Search FAQs by keyword"""
    try:
        query = request.args.get('q', '')
        
        if not query:
            return error_response('Search query required', 400)
        
        with get_db_session() as db:
            # Use SystemSettingService instead of FAQService
            setting_service = SystemSettingService()
            faqs = setting_service.search_faqs(db, query, active_only=True)
            
            return success_response(
                message=f'Found {len(faqs)} FAQ(s)',
                data=[{
                    'id': faq.id,
                    'question': faq.question,
                    'answer': faq.answer,
                    'category_id': faq.category_id,
                    'category_name': faq.faq_category.name if faq.faq_category else None
                } for faq in faqs]
            )
                
    except Exception as e:
        print(f"❌ Error in search_faqs: {str(e)}")
        traceback.print_exc()
        return error_response(str(e), 500)

@bot_api_bp.route('/bot/chat/broadcast-message', methods=['POST'])
def broadcast_message():
    """Broadcast message to admins via WebSocket - calls web app endpoint"""
    try:
        import requests
        import os
        
        data = request.json
        required_fields = ['session_id', 'user_id', 'message']
        
        if not all(field in data for field in required_fields):
            return error_response('Missing required fields', 400)
        
        # Call the web app's broadcast endpoint
        web_url = os.getenv('WEB_BASE_URL', 'http://127.0.0.1:5000')
        broadcast_url = f"{web_url}/portal/admin/api/broadcast-message"
        
        try:
            response = requests.post(
                broadcast_url,
                json=data,
                timeout=2  # Short timeout since it's internal
            )
            
            if response.status_code == 200:
                print(f"Message broadcasted successfully via web app")
                return success_response(message='Message broadcasted successfully')
            else:
                print(f"⚠️ Broadcast failed: {response.status_code}")
                # Don't fail the request, just log it
                return success_response(message='Message received but broadcast failed')
                
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Could not reach web app for broadcasting: {e}")
            # Don't fail - the message is still saved, just no real-time update
            return success_response(message='Message received')
                
    except Exception as e:
        print(f"❌ Error in broadcast_message: {str(e)}")
        traceback.print_exc()
        return error_response(str(e), 500)

@bot_api_bp.route('/bot/chat/broadcast-new-session', methods=['POST'])
def broadcast_new_session():
    """Broadcast new session creation to all admins - calls web app endpoint"""
    try:
        import requests
        import os
        
        data = request.json
        required_fields = ['session_id', 'user_id']
        
        if not all(field in data for field in required_fields):
            return error_response('Missing required fields', 400)
        
        # Call the web app's broadcast endpoint
        web_url = os.getenv('WEB_BASE_URL', 'http://127.0.0.1:5000')
        broadcast_url = f"{web_url}/portal/admin/api/broadcast-new-session"
        
        try:
            response = requests.post(
                broadcast_url,
                json=data,
                timeout=2  # Short timeout since it's internal
            )
            
            if response.status_code == 200:
                print(f"New session broadcasted successfully via web app")
                return success_response(message='New session broadcasted successfully')
            else:
                print(f"⚠️ Broadcast failed: {response.status_code}")
                return success_response(message='Session created but broadcast failed')
                
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Could not reach web app for broadcasting: {e}")
            return success_response(message='Session created')
                
    except Exception as e:
        print(f"❌ Error in broadcast_new_session: {str(e)}")
        traceback.print_exc()
        return error_response(str(e), 500)