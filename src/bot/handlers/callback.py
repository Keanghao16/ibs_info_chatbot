from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ...database.connection import SessionLocal
from ...database.models import ChatSession, User, Admin, AdminRole
from ...services.user_service import create_user

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    db = SessionLocal()
    try:
        user_id = query.from_user.id
        telegram_user = query.from_user
        
        # Check if user exists, if not create them
        user = db.query(User).filter(User.telegram_id == str(user_id)).first()
        
        if not user:
            # Create user if they don't exist
            user_data = {
                "telegram_id": str(user_id),
                "full_name": telegram_user.full_name or f"{telegram_user.first_name} {telegram_user.last_name or ''}".strip(),
                "username": telegram_user.username,
                "is_active": True
            }
            user = create_user(db, user_data)

        if query.data == "start_chat":
            if user:
                # Find available admin (agent)
                available_admin = db.query(Admin).filter(
                    Admin.role == AdminRole.admin,
                    Admin.is_available == True,
                    Admin.is_active == True
                ).first()
                
                if available_admin:
                    # Create a new chat session
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
            faq_text = "📚 **Frequently Asked Questions**\n\nPlease select a question:"
            
            # Create FAQ question buttons
            faq_keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("❓ How do I start a chat?", callback_data='faq_start_chat')],
                [InlineKeyboardButton("❓ How do I contact support?", callback_data='faq_contact_support')],
                [InlineKeyboardButton("❓ What are your operating hours?", callback_data='faq_operating_hours')],
                [InlineKeyboardButton("❓ How do I view my chat history?", callback_data='faq_chat_history')],
                [InlineKeyboardButton("🔙 Back to Main Menu", callback_data='back_to_main')]
            ])
            await query.edit_message_text(faq_text, parse_mode='Markdown', reply_markup=faq_keyboard)

        # FAQ Answer handlers
        elif query.data == "faq_start_chat":
            answer = """
❓ **How do I start a chat?**

To start a chat session:
1. Click on "💬 Start Chat" button from the main menu
2. You will be connected to an available agent
3. Start typing your message to begin the conversation
            """
            back_keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to FAQ", callback_data='faq')],
                [InlineKeyboardButton("🏠 Main Menu", callback_data='back_to_main')]
            ])
            await query.edit_message_text(answer, parse_mode='Markdown', reply_markup=back_keyboard)

        elif query.data == "faq_contact_support":
            answer = """
❓ **How do I contact support?**

To contact our support team:
1. Use the chat feature by clicking "💬 Start Chat"
2. An agent will assist you with your inquiry
3. You can also send us a direct message anytime
4. For urgent matters, mention "URGENT" in your message
            """
            back_keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to FAQ", callback_data='faq')],
                [InlineKeyboardButton("🏠 Main Menu", callback_data='back_to_main')]
            ])
            await query.edit_message_text(answer, parse_mode='Markdown', reply_markup=back_keyboard)

        elif query.data == "faq_operating_hours":
            answer = """
❓ **What are your operating hours?**

Our support is available:
🕐 **24/7** - Round the clock support
📅 **7 days a week** - Including weekends
🚀 **Instant response** - Average response time: 2-5 minutes
🌍 **Global coverage** - Support in multiple time zones
            """
            back_keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to FAQ", callback_data='faq')],
                [InlineKeyboardButton("🏠 Main Menu", callback_data='back_to_main')]
            ])
            await query.edit_message_text(answer, parse_mode='Markdown', reply_markup=back_keyboard)

        elif query.data == "faq_chat_history":
            answer = """
❓ **How do I view my chat history?**

To access your chat history:
1. Click "📜 View Chat History" from the main menu
2. You'll see all your previous conversations
3. Each session shows the agent and timestamp
4. You can review past conversations anytime
            """
            back_keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to FAQ", callback_data='faq')],
                [InlineKeyboardButton("🏠 Main Menu", callback_data='back_to_main')]
            ])
            await query.edit_message_text(answer, parse_mode='Markdown', reply_markup=back_keyboard)

        elif query.data == "view_chat_history":
            if user:
                chat_sessions = db.query(ChatSession).filter(ChatSession.user_id == user.id).all()
                if chat_sessions:
                    history_text = f"📝 **Your Chat History ({len(chat_sessions)} sessions):**\n\n"
                    for i, session in enumerate(chat_sessions[-5:], 1):  # Show last 5 sessions
                        agent_name = session.agent.name if session.agent else "System"
                        status = session.status.value if session.status else "unknown"
                        start_time = session.start_time.strftime('%Y-%m-%d %H:%M') if session.start_time else 'Unknown'
                        history_text += f"{i}. **Agent:** {agent_name}\n   **Date:** {start_time}\n   **Status:** {status.title()}\n\n"
                else:
                    history_text = "📝 No chat history found.\n\nStart your first conversation by clicking '💬 Start Chat'!"
                
                # Create back button
                history_keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back to Main Menu", callback_data='back_to_main')]
                ])
                await query.edit_message_text(history_text, parse_mode='Markdown', reply_markup=history_keyboard)
            else:
                await query.edit_message_text("❌ User not found. Please use /start first.")
        
        elif query.data == "manage_users":
            admin_keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("👥 View All Users", callback_data='view_users')],
                [InlineKeyboardButton("🚫 Block User", callback_data='block_user')],
                [InlineKeyboardButton("🔙 Back to Main Menu", callback_data='back_to_main')]
            ])
            await query.edit_message_text("🔧 **Admin Panel**\n\nSelect an option:", parse_mode='Markdown', reply_markup=admin_keyboard)

        elif query.data == "back_to_main":
            # Import main_keyboard here to avoid circular imports
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
        await query.edit_message_text("❌ Sorry, there was an error processing your request.")
    finally:
        db.close()