from telegram import Update
from telegram.ext import ContextTypes
from ...database.connection import SessionLocal
from ...database.models import ChatMessage, User
from ...services.user_service import create_user

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message_text = update.message.text
    telegram_user = update.effective_user

    db = SessionLocal()
    try:
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
            await update.message.reply_text(
                "Welcome! I've registered you in our system. "
                "Please use /start to see available options."
            )
        else:
            # Save the message
            chat_message = ChatMessage(
                user_id=user.id,
                message=message_text,
                timestamp=update.message.date
            )
            db.add(chat_message)
            db.commit()
            await update.message.reply_text("Message received! How can I help you today?")
            
    except Exception as e:
        print(f"Error handling message: {e}")
        await update.message.reply_text("Sorry, there was an error processing your message.")
    finally:
        db.close()