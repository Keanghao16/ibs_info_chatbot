# ============================================================================
# FILE: src/bot/handlers/message.py
# FIXED VERSION - Proper session handling and error reporting
# ============================================================================

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ...database.connection import SessionLocal
from ...database.models import ChatMessage, SessionStatus, ChatSession
from ...services import UserService
from ...utils.bot_api_client import bot_api_client
from datetime import datetime
user_service = UserService()

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message_text = update.message.text
    telegram_user = update.effective_user

    db = SessionLocal()
    try:
        # Get user profile photo
        photo_url = None
        try:
            photos = await context.bot.get_user_profile_photos(telegram_user.id, limit=1)
            if photos.total_count > 0:
                photo = photos.photos[0][-1]
                file = await context.bot.get_file(photo.file_id)
                photo_url = file.file_path
        except Exception as e:
            print(f"Error fetching user photo: {e}")
        
        # Check if user is admin
        result = user_service.get_user_or_admin_by_telegram_id(db, str(telegram_user.id))
        is_admin = result and result['type'] == "admin"
        
        # ✅ Allow admins to search FAQs
        if is_admin and context.user_data.get('searching_faq'):
            context.user_data['searching_faq'] = False
            
            # Call API for FAQ search
            response = bot_api_client.get('/bot/faq/search', {'q': message_text})
            
            if not response.get('success'):
                await update.message.reply_text(
                    "❌ Unable to search FAQs. Please try again later.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("📚 Browse Categories", callback_data='faq')],
                        [InlineKeyboardButton("🏠 Main Menu", callback_data='back_to_main')]
                    ])
                )
                return
            
            search_results = response.get('data', [])
            
            if not search_results:
                await update.message.reply_text(
                    f"🔍 No results found for: *{message_text}*\n\n"
                    f"Try different keywords or browse categories.",
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("📚 Browse Categories", callback_data='faq')],
                        [InlineKeyboardButton("🏠 Main Menu", callback_data='back_to_main')]
                    ])
                )
            else:
                # Show search results
                keyboard = []
                for faq in search_results[:10]:
                    question_preview = faq['question'][:50] + "..." if len(faq['question']) > 50 else faq['question']
                    keyboard.append([InlineKeyboardButton(
                        f"❓ {question_preview}",
                        callback_data=f"faq_view_{faq['id']}"
                    )])
                
                keyboard.append([InlineKeyboardButton("🔍 Search Again", callback_data='faq_search')])
                keyboard.append([InlineKeyboardButton("📚 Browse Categories", callback_data='faq')])
                keyboard.append([InlineKeyboardButton("🏠 Main Menu", callback_data='back_to_main')])
                
                await update.message.reply_text(
                    f"🔍 Found {len(search_results)} result(s) for: *{message_text}*\n\n"
                    f"Select a question to view the answer:",
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            return
        
        # ✅ Block admins from regular chat (but not FAQ search)
        if is_admin:
            await update.message.reply_text(
                "⚠️ You're logged in as an admin.\n"
                "Please use the admin panel to manage chats.\n\n"
                "Use /start to access admin features."
            )
            return
        
        # 🆕 Use UserService method to create user if doesn't exist
        create_result = user_service.create_user_if_not_admin(
            db=db,
            telegram_id=str(telegram_user.id),
            username=telegram_user.username,
            first_name=telegram_user.first_name,
            last_name=telegram_user.last_name,
            full_name=telegram_user.full_name,
            photo_url=photo_url
        )
        
        if not create_result['success'] and 'admin' not in create_result['message'].lower():
            await update.message.reply_text(
                "⚠️ Please use /start first to initialize your account."
            )
            return
        
        # Get the user object
        user = create_result.get('user') or user_service.get_user_by_telegram_id(db, str(telegram_user.id))
        
        if not user:
            await update.message.reply_text(
                "⚠️ Please use /start first to initialize your account."
            )
            return
        
        # 🆕 Check if user is searching FAQs
        if context.user_data.get('searching_faq'):
            context.user_data['searching_faq'] = False
        
            response = bot_api_client.get('/bot/faq/search', {'q': message_text})
            
            if not response.get('success'):
                await update.message.reply_text(
                    "❌ Unable to search FAQs. Please try again later.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("📚 Browse Categories", callback_data='faq')],
                        [InlineKeyboardButton("🏠 Main Menu", callback_data='back_to_main')]
                    ])
                )
                return
            
            search_results = response.get('data', [])
            
            if not search_results:
                await update.message.reply_text(
                    f"🔍 No results found for: *{message_text}*\n\n"
                    f"Try different keywords or browse categories.",
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("📚 Browse Categories", callback_data='faq')],
                        [InlineKeyboardButton("💬 Start Chat", callback_data='start_chat')],
                        [InlineKeyboardButton("🏠 Main Menu", callback_data='back_to_main')]
                    ])
                )
            else:
                keyboard = []
                for faq in search_results[:10]:
                    question_preview = faq['question'][:50] + "..." if len(faq['question']) > 50 else faq['question']
                    keyboard.append([InlineKeyboardButton(
                        f"❓ {question_preview}",
                        callback_data=f"faq_view_{faq['id']}"
                    )])
                
                keyboard.append([InlineKeyboardButton("🔍 Search Again", callback_data='faq_search')])
                keyboard.append([InlineKeyboardButton("📚 Browse Categories", callback_data='faq')])
                keyboard.append([InlineKeyboardButton("🏠 Main Menu", callback_data='back_to_main')])
                
                await update.message.reply_text(
                    f"🔍 Found {len(search_results)} result(s) for: *{message_text}*\n\n"
                    f"Select a question to view the answer:",
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            
            user.last_activity = datetime.now()
            db.commit()
            return
        
        # 🆕 AUTO-CREATE SESSION: Check for active session or create new one
        active_session = db.query(ChatSession).filter(
            ChatSession.user_id == user.id,
            ChatSession.status.in_([SessionStatus.waiting, SessionStatus.active])
        ).first()
        
        # 🔧 FIX: Create session if it doesn't exist
        if not active_session:
            print(f"📝 Creating new session for user {user.full_name}")
            active_session = ChatSession(
                user_id=user.id,
                status=SessionStatus.waiting
            )
            db.add(active_session)
            db.flush()  # 🔧 FIX: Use flush() to get the ID without committing
            
            print(f"✅ Auto-created session #{active_session.id} for user {user.full_name}")
            
            # 🆕 Broadcast new session to all admins
            broadcast_session_response = bot_api_client.post('/bot/chat/broadcast-new-session', {
                'session_id': active_session.id,
                'user_id': str(user.id),
                'user_name': user.full_name
            })
            
            if broadcast_session_response.get('success'):
                print(f"✅ New session broadcasted to all admins")
            
            await update.message.reply_text(
                "✅ Your chat session has been started!\n"
                "An agent will be with you shortly. You can continue sending messages."
            )
        
        # 🔧 FIX: Ensure session_id is available
        if not active_session.id:
            db.flush()  # Force flush to get the ID
        
        print(f"💬 Saving message to session #{active_session.id} from user {user.full_name}")
        
        # 🆕 Save message WITH session_id
        chat_message = ChatMessage(
            session_id=active_session.id,
            user_id=str(user.id),
            admin_id=str(active_session.admin_id) if active_session.admin_id else None,
            message=message_text,
            is_from_admin=False,
            timestamp=datetime.now()  
        )
        db.add(chat_message)
        
        # Update last activity
        user.last_activity = datetime.now()
        
        # 🔧 FIX: Commit everything together
        db.commit()
        
        print(f"✅ Message saved successfully to session #{active_session.id}")
        
        # 🆕 Notify admin via API (which will broadcast via WebSocket)
        if active_session.admin_id:
            # Broadcast to assigned admin
            broadcast_response = bot_api_client.post('/bot/chat/broadcast-message', {
                'session_id': active_session.id,
                'user_id': str(user.id),
                'user_name': user.full_name,
                'message': message_text,
                'admin_id': str(active_session.admin_id)
            })
            
            if broadcast_response.get('success'):
                print(f"✅ Message broadcasted to admin {active_session.admin_id}")
            
            await update.message.reply_text(
                "✅ Your message has been sent to our support agent."
            )
        else:
            # Session is waiting - broadcast to all admins
            broadcast_response = bot_api_client.post('/bot/chat/broadcast-message', {
                'session_id': active_session.id,
                'user_id': str(user.id),
                'user_name': user.full_name,
                'message': message_text
            })
            
            if broadcast_response.get('success'):
                print(f"✅ New waiting session broadcasted to all admins")
            
            await update.message.reply_text(
                "📝 Message received! An agent will be with you soon."
            )
            
    except Exception as e:
        print(f"❌ Error handling message: {e}")
        import traceback
        traceback.print_exc()
        
        # 🔧 FIX: Better error message with details
        error_message = f"Sorry, there was an error processing your message.\n\nError: {str(e)}"
        await update.message.reply_text(error_message[:500])  # Limit message length
    finally:
        db.close()