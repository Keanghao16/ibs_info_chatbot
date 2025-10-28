from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ...database.connection import SessionLocal
from ...database.models import ChatMessage, User, SessionStatus, ChatSession  # Add ChatSession
from ...services.user_service import UserService
from ...services.faq_service import FAQService
from ...web.websocket_manager import broadcast_new_message
from datetime import datetime, timezone  # Add timezone import

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message_text = update.message.text
    telegram_user = update.effective_user

    db = SessionLocal()
    try:
        # Get user profile photo if not already saved
        photo_url = None
        try:
            photos = await context.bot.get_user_profile_photos(telegram_user.id, limit=1)
            if photos.total_count > 0:
                photo = photos.photos[0][-1]  # Get largest size
                file = await context.bot.get_file(photo.file_id)
                photo_url = file.file_path
        except Exception as e:
            print(f"Error fetching user photo: {e}")
        
        # Create user data object with photo
        class TelegramUserData:
            def __init__(self, telegram_user, photo_url=None):
                self.id = telegram_user.id
                self.username = telegram_user.username
                self.first_name = telegram_user.first_name
                self.last_name = telegram_user.last_name
                self.photo_url = photo_url
        
        user_data = TelegramUserData(telegram_user, photo_url)
        
        # Create UserService instance and use it
        user_service = UserService()
        user = user_service.find_or_create_user(db, user_data)
        
        # Check for active chat session
        active_session = db.query(ChatSession).filter(
            ChatSession.user_id == user.id,
            ChatSession.status == SessionStatus.active
        ).first()
        
        if active_session:
            # Save message to active session
            chat_message = ChatMessage(
                user_id=user.id,
                admin_id=active_session.admin_id,
                message=message_text,
                is_from_admin=False,
                timestamp=update.message.date  # This already has timezone from Telegram
            )
            db.add(chat_message)
            db.commit()
            
            # Broadcast to admin via WebSocket
            if active_session.admin_id:
                broadcast_new_message(
                    user.id, 
                    message_text, 
                    active_session.admin_id,
                    active_session.id
                )
            
            await update.message.reply_text(
                "✅ Your message has been sent to our support agent."
            )
        else:
            # Check if user is searching FAQs
            if context.user_data.get('searching_faq'):
                context.user_data['searching_faq'] = False
            
                # Search FAQs
                faq_service = FAQService()
                search_results = faq_service.search_faqs(db, message_text)
                
                if not search_results:
                    await update.message.reply_text(
                        f"🔍 **Search Results for:** '{message_text}'\n\n"
                        "❌ No matching FAQs found.\n\n"
                        "Try different keywords or browse FAQ categories.",
                        parse_mode='Markdown',
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("📚 Browse FAQs", callback_data='faq')],
                            [InlineKeyboardButton("💬 Contact Support", callback_data='start_chat')]
                        ])
                    )
                else:
                    # Show search results
                    keyboard = []
                    for faq in search_results[:10]:  # Limit to 10 results
                        question_preview = faq.question[:60] + "..." if len(faq.question) > 60 else faq.question
                        keyboard.append([
                            InlineKeyboardButton(
                                f"❓ {question_preview}",
                                callback_data=f'faq_view_{faq.id}'
                            )
                        ])
                    
                    keyboard.append([InlineKeyboardButton("🔙 Back to FAQ", callback_data='faq')])
                    
                    result_text = f"🔍 **Search Results for:** '{message_text}'\n\n"
                    result_text += f"Found {len(search_results)} matching FAQ(s):"
                    
                    await update.message.reply_text(
                        result_text,
                        parse_mode='Markdown',
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
                
                # Update last activity
                user.last_activity = datetime.now()
                db.commit()
                return
            
            # Save the message
            chat_message = ChatMessage(
                user_id=user.id,
                message=message_text,
                timestamp=update.message.date  # This already has timezone
            )
            db.add(chat_message)
            
            # Update last activity
            user.last_activity = datetime.now()
            db.commit()
            
            await update.message.reply_text("Message received! How can I help you today?")
            
    except Exception as e:
        print(f"Error handling message: {e}")
        import traceback
        traceback.print_exc()
        await update.message.reply_text("Sorry, there was an error processing your message.")
    finally:
        db.close()