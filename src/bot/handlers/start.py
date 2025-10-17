from telegram import Update
from telegram.ext import ContextTypes
from ..keyboards.inline import main_keyboard
from ...database.connection import SessionLocal
from ...services.user_service import create_user, get_user_by_id
from ...database.models import User

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Save or update user information in database
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.telegram_id == str(user.id)).first()
        
        if not existing_user:
            # Create new user
            user_data = {
                "telegram_id": str(user.id),
                "full_name": user.full_name or f"{user.first_name} {user.last_name or ''}".strip(),
                "username": user.username,
                "is_active": True
            }
            create_user(db, user_data)
            welcome_message = f"👋 Welcome {user.first_name}! You've been registered successfully."
        else:
            # Update existing user info if changed
            updated = False
            if existing_user.full_name != (user.full_name or f"{user.first_name} {user.last_name or ''}".strip()):
                existing_user.full_name = user.full_name or f"{user.first_name} {user.last_name or ''}".strip()
                updated = True
            if existing_user.username != user.username:
                existing_user.username = user.username
                updated = True
            if not existing_user.is_active:
                existing_user.is_active = True
                updated = True
                
            if updated:
                db.commit()
            
            welcome_message = f"👋 Welcome back {user.first_name}!"
        
        await update.message.reply_text(
            f"{welcome_message}\n"
            "Use the buttons below to navigate.",
            reply_markup=main_keyboard()
        )
        
    except Exception as e:
        print(f"Error saving user: {e}")
        await update.message.reply_text(
            f"👋 Hello {user.first_name}! Welcome to our Telegram bot. "
            "Use the buttons below to navigate.",
            reply_markup=main_keyboard()
        )
    finally:
        db.close()