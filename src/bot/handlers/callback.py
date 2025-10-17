from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ...database.connection import SessionLocal
from ...database.models import ChatSession, User, Admin, AdminRole, FAQ
from ...services.user_service import find_or_create_user
from ...services.faq_service import FAQService

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    db = SessionLocal()
    try:
        user_id = query.from_user.id
        telegram_user = query.from_user
        
        # Get user profile photo if not already saved
        photo_url = None
        try:
            photos = await context.bot.get_user_profile_photos(telegram_user.id, limit=1)
            if photos.total_count > 0:
                photo = photos.photos[0][-1]
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
        user = find_or_create_user(db, user_data)

        if query.data == "start_chat":
            if user:
                available_admin = db.query(Admin).filter(
                    Admin.role == AdminRole.admin,
                    Admin.is_available == True,
                    Admin.is_active == True
                ).first()
                
                if available_admin:
                    from ...database.models import SessionStatus
                    new_session = ChatSession(
                        user_id=user.id,
                        admin_id=available_admin.id,
                        status=SessionStatus.active
                    )
                    db.add(new_session)
                    db.commit()
                    
                    await query.edit_message_text(
                        f"✅ Chat session started! You've been connected to {available_admin.full_name} "
                        f"from {available_admin.division or 'Support Team'}."
                    )
                else:
                    await query.edit_message_text(
                        "❌ Sorry, no agents are available at the moment. Please try again later."
                    )
            else:
                await query.edit_message_text("❌ Please use /start first to register.")
            
        elif query.data == "faq":
            # Get FAQ categories dynamically
            faq_service = FAQService()
            categories = faq_service.get_all_categories(db)
            
            if not categories:
                await query.edit_message_text(
                    "📚 **FAQ Section**\n\n"
                    "No FAQs available at the moment. Please contact support for assistance.",
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data='back_to_main')]
                    ])
                )
                return
            
            # Create category buttons dynamically
            keyboard = []
            for category in categories:
                # Count FAQs in this category
                faqs_count = len(faq_service.get_faqs_by_category(db, category))
                category_label = category.replace('_', ' ').title()
                keyboard.append([
                    InlineKeyboardButton(
                        f"📁 {category_label} ({faqs_count})",
                        callback_data=f'faq_cat_{category}'
                    )
                ])
            
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
            # Show FAQs for selected category
            category = query.data.replace("faq_cat_", "")
            faq_service = FAQService()
            faqs = faq_service.get_faqs_by_category(db, category)
            
            if not faqs:
                await query.edit_message_text(
                    f"📚 **{category.replace('_', ' ').title()}**\n\n"
                    "No FAQs found in this category.",
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 Back to FAQ", callback_data='faq')]
                    ])
                )
                return
            
            # Create FAQ question buttons
            keyboard = []
            for faq in faqs:
                # Truncate question if too long
                question_preview = faq.question[:60] + "..." if len(faq.question) > 60 else faq.question
                keyboard.append([
                    InlineKeyboardButton(
                        f"❓ {question_preview}",
                        callback_data=f'faq_view_{faq.id}'
                    )
                ])
            
            keyboard.append([InlineKeyboardButton("🔙 Back to FAQ Categories", callback_data='faq')])
            keyboard.append([InlineKeyboardButton("🏠 Main Menu", callback_data='back_to_main')])
            
            category_label = category.replace('_', ' ').title()
            text = f"📚 **{category_label}**\n\n"
            text += f"Found {len(faqs)} FAQ(s) in this category. Select a question:"
            
            await query.edit_message_text(
                text,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        elif query.data.startswith("faq_view_"):
            # Show specific FAQ answer
            faq_id = int(query.data.replace("faq_view_", ""))
            faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
            
            if not faq:
                await query.edit_message_text(
                    "❌ FAQ not found.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 Back to FAQ", callback_data='faq')]
                    ])
                )
                return
            
            # Format the FAQ answer
            answer_text = f"❓ **{faq.question}**\n\n"
            answer_text += faq.answer
            
            # Add category tag
            category_label = faq.category.replace('_', ' ').title()
            answer_text += f"\n\n📁 Category: {category_label}"
            
            keyboard = [
                [InlineKeyboardButton("🔙 Back to Category", callback_data=f'faq_cat_{faq.category}')],
                [InlineKeyboardButton("📚 All FAQs", callback_data='faq')],
                [InlineKeyboardButton("🏠 Main Menu", callback_data='back_to_main')]
            ]
            
            await query.edit_message_text(
                answer_text,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        elif query.data == "faq_search":
            # Prompt user to search
            await query.edit_message_text(
                "🔍 **Search FAQs**\n\n"
                "Please type your search query in the chat.\n"
                "I'll search through all FAQs and show you relevant results.\n\n"
                "Example: Type 'payment' to find FAQs about payments.",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back to FAQ", callback_data='faq')],
                    [InlineKeyboardButton("🏠 Main Menu", callback_data='back_to_main')]
                ])
            )
            
            # Store in context that user wants to search FAQs
            context.user_data['searching_faq'] = True

        elif query.data == "view_chat_history":
            if user:
                chat_sessions = db.query(ChatSession).filter(ChatSession.user_id == user.id).all()
                if chat_sessions:
                    history_text = f"📝 **Your Chat History ({len(chat_sessions)} sessions):**\n\n"
                    for i, session in enumerate(chat_sessions[-5:], 1):
                        agent_name = session.admin.full_name if session.admin else "System"
                        status = session.status.value if session.status else "unknown"
                        start_time = session.start_time.strftime('%Y-%m-%d %H:%M') if session.start_time else 'Unknown'
                        history_text += f"{i}. **Agent:** {agent_name}\n   **Date:** {start_time}\n   **Status:** {status.title()}\n\n"
                else:
                    history_text = "📝 No chat history found.\n\nStart your first conversation by clicking '💬 Start Chat'!"
                
                history_keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back to Main Menu", callback_data='back_to_main')]
                ])
                await query.edit_message_text(history_text, parse_mode='Markdown', reply_markup=history_keyboard)
            else:
                await query.edit_message_text("❌ User not found. Please use /start first.")

        elif query.data == "back_to_main":
            from ..keyboards.inline import main_keyboard
            await query.edit_message_text(
                f"👋 Hello {telegram_user.first_name}! Welcome back to our Telegram bot.\n"
                "Use the buttons below to navigate.",
                reply_markup=main_keyboard()
            )
            
        else:
            await query.edit_message_text("❌ Unknown action. Please try again.")
            
    except Exception as e:
        print(f"Error in callback handler: {e}")
        import traceback
        traceback.print_exc()
        await query.edit_message_text("❌ Sorry, there was an error processing your request.")
    finally:
        db.close()