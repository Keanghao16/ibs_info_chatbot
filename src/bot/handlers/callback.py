from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ...database.connection import SessionLocal
from ...database.models import ChatSession, Admin, AdminRole, SessionStatus
from ...services import UserService
from ...utils.bot_api_client import bot_api_client

user_service = UserService()

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    db = SessionLocal()
    try:
        telegram_user = query.from_user
        
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
        
        # Use UserService method to check if user or admin
        result = user_service.get_user_or_admin_by_telegram_id(db, str(telegram_user.id))
        
        is_admin = result and result['type'] == "admin"
        
        # ✅ REMOVED the admin restriction - admins can now use FAQ features
        # Only restrict chat functionality for admins
        if is_admin and query.data == "start_chat":
            await query.edit_message_text(
                "⚠️ Admin accounts cannot start chat sessions.\n"
                "Please use the admin panel to manage chats."
            )
            return
        
        # For non-admins, ensure user exists
        if not is_admin:
            create_result = user_service.create_user_if_not_admin(
                db=db,
                telegram_id=str(telegram_user.id),
                username=telegram_user.username,
                first_name=telegram_user.first_name,
                last_name=telegram_user.last_name,
                full_name=telegram_user.full_name,
                photo_url=photo_url
            )
            
            if not create_result['success']:
                await query.edit_message_text("⚠️ Please use /start first.")
                return
            
            user = create_result.get('user') or user_service.get_user_by_telegram_id(db, str(telegram_user.id))
        else:
            user = None  # Admin doesn't need user object for FAQ browsing

        if query.data == "start_chat":
            if user:
                # Check for existing active session
                active_session = db.query(ChatSession).filter(
                    ChatSession.user_id == user.id,
                    ChatSession.status == SessionStatus.active
                ).first()
                
                if active_session:
                    await query.edit_message_text(
                        "✅ You already have an active chat session.\n"
                        "Please continue chatting or wait for an admin to respond."
                    )
                else:
                    # Create new session
                    new_session = ChatSession(user_id=user.id, status=SessionStatus.waiting)
                    db.add(new_session)
                    db.commit()
                    
                    await query.edit_message_text(
                        "✅ Chat session started!\n"
                        "An admin will be with you shortly. Please type your message."
                    )
            else:
                await query.edit_message_text("⚠️ Please use /start first.")
            
        elif query.data == "faq":
            # ✅ FAQ accessible to both users and admins
            response = bot_api_client.get('/bot/faq/categories')
            
            if not response.get('success'):
                await query.edit_message_text(
                    "❌ Unable to load FAQ categories. Please try again later."
                )
                return
            
            categories = response.get('data', [])
            
            if not categories:
                await query.edit_message_text(
                    "📚 No FAQ categories available at the moment.\n\n"
                    "Please check back later or contact support directly.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data='back_to_main')]
                    ])
                )
                return
            
            # Create category buttons dynamically
            keyboard = []
            for category in categories:
                faq_count = category.get('faq_count', 0)
                icon = category.get('icon', '📁')
                button_text = f"{icon} {category['name']} ({faq_count})"
                keyboard.append([InlineKeyboardButton(
                    button_text,
                    callback_data=f"faq_cat_{category['id']}"
                )])
            
            # Add search and back buttons
            keyboard.append([InlineKeyboardButton("🔍 Search FAQs", callback_data='faq_search')])
            keyboard.append([InlineKeyboardButton("🔙 Back to Main Menu", callback_data='back_to_main')])
            
            faq_text = "📚 **Frequently Asked Questions**\n\n"
            faq_text += "Please select a category or search for specific topics:"
            
            await query.edit_message_text(
                faq_text,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        elif query.data.startswith("faq_cat_"):
            # ✅ Show FAQs for selected category - accessible to both users and admins
            category_id = int(query.data.replace("faq_cat_", ""))
            
            response = bot_api_client.get(f'/bot/faq/category/{category_id}')
            
            if not response.get('success'):
                await query.edit_message_text(
                    "❌ Unable to load FAQs. Please try again later.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 Back to FAQ Categories", callback_data='faq')]
                    ])
                )
                return
            
            data = response.get('data', {})
            category = data.get('category', {})
            faqs = data.get('faqs', [])
            
            if not faqs:
                await query.edit_message_text(
                    f"📁 **{category.get('name', 'Category')}**\n\n"
                    f"No FAQs available in this category yet.",
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 Back to FAQ Categories", callback_data='faq')],
                        [InlineKeyboardButton("🏠 Main Menu", callback_data='back_to_main')]
                    ])
                )
                return
            
            # Create FAQ question buttons
            keyboard = []
            for faq in faqs:
                # Truncate long questions for button text
                question_preview = faq['question'][:50] + "..." if len(faq['question']) > 50 else faq['question']
                keyboard.append([InlineKeyboardButton(
                    f"❓ {question_preview}",
                    callback_data=f"faq_view_{faq['id']}"
                )])
            
            keyboard.append([InlineKeyboardButton("🔙 Back to FAQ Categories", callback_data='faq')])
            keyboard.append([InlineKeyboardButton("🏠 Main Menu", callback_data='back_to_main')])
            
            icon = category.get('icon', '📁')
            text = f"{icon} **{category.get('name', 'Category')}**\n\n"
            if category.get('description'):
                text += f"{category['description']}\n\n"
            text += f"Found {len(faqs)} FAQ(s) in this category. Select a question:"
            
            await query.edit_message_text(
                text,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        elif query.data.startswith("faq_view_"):
            # ✅ Show specific FAQ answer - accessible to both users and admins
            faq_id = int(query.data.replace("faq_view_", ""))
            
            response = bot_api_client.get(f'/bot/faq/{faq_id}')
            
            if not response.get('success'):
                await query.edit_message_text(
                    "❌ Unable to load FAQ. Please try again later.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 Back to FAQ Categories", callback_data='faq')]
                    ])
                )
                return
            
            faq = response.get('data', {})
            
            text = f"❓ **{faq.get('question', 'Question')}**\n\n"
            text += f"💡 {faq.get('answer', 'No answer available.')}"
            
            keyboard = [
                [InlineKeyboardButton("🔙 Back to Category", callback_data=f"faq_cat_{faq.get('category_id')}")],
                [InlineKeyboardButton("📚 All Categories", callback_data='faq')],
                [InlineKeyboardButton("🏠 Main Menu", callback_data='back_to_main')]
            ]
            
            await query.edit_message_text(
                text,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        elif query.data == "faq_search":
            # ✅ FAQ search - accessible to both users and admins
            context.user_data['searching_faq'] = True
            await query.edit_message_text(
                "🔍 **FAQ Search**\n\n"
                "Please type your search query (keywords or question).\n\n"
                "I'll search through all FAQs and show you relevant results.",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("❌ Cancel Search", callback_data='faq')]
                ])
            )

        elif query.data == "view_chat_history":
            # This would show previous chats - implement as needed
            await query.edit_message_text(
                "📜 **Chat History**\n\n"
                "This feature will show your previous conversations with support.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back to Main Menu", callback_data='back_to_main')]
                ])
            )

        elif query.data == "back_to_main":
            # ✅ Return appropriate keyboard based on user type
            if is_admin:
                from ..keyboards.inline import admin_keyboard
                await query.edit_message_text(
                    f"👋 Welcome back, Admin {telegram_user.first_name}!\n\n"
                    "What would you like to do?",
                    reply_markup=admin_keyboard()
                )
            else:
                from ..keyboards.inline import main_keyboard
                await query.edit_message_text(
                    f"👋 Welcome back, {telegram_user.first_name}!\n\n"
                    "What would you like to do?",
                    reply_markup=main_keyboard()
                )
            
        else:
            await query.edit_message_text("Unknown action.")
            
    except Exception as e:
        print(f"Error in callback handler: {e}")
        import traceback
        traceback.print_exc()
        await query.edit_message_text("❌ Sorry, there was an error processing your request.")
    finally:
        db.close()