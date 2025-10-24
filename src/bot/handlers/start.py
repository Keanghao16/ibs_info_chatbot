from telegram import Update
from telegram.ext import ContextTypes
from ..keyboards.inline import main_keyboard
from ...database.connection import SessionLocal
from ...services.user_service import UserService
from ...database.models import User
from datetime import datetime

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Save or update user information in database
    db = SessionLocal()
    try:
        # Get user profile photos
        photo_url = None
        try:
            photos = await context.bot.get_user_profile_photos(user.id, limit=1)
            if photos.total_count > 0:
                # Get the first (current) profile photo - use the largest size
                photo = photos.photos[0][-1]  # Get largest size (last in array)
                file = await context.bot.get_file(photo.file_id)
                photo_url = file.file_path
                print(f"User photo URL: {photo_url}")  # Debug
        except Exception as e:
            print(f"Error fetching user photo: {e}")
        
        # Create a user data object with photo
        class TelegramUserData:
            def __init__(self, telegram_user, photo_url=None):
                self.id = telegram_user.id
                self.username = telegram_user.username
                self.first_name = telegram_user.first_name
                self.last_name = telegram_user.last_name
                self.photo_url = photo_url
        
        user_data = TelegramUserData(user, photo_url)
        
        # Create UserService instance and use it
        user_service = UserService()
        existing_user = user_service.find_or_create_user(db, user_data)
        
        # Check if this is a new user (just created)
        is_new_user = existing_user.created_at and (
            datetime.now() - existing_user.created_at.replace(tzinfo=None)
        ).total_seconds() < 5  # Created within last 5 seconds
        
        if is_new_user:
            welcome_message = f"👋 Welcome {user.first_name}! You've been registered successfully."
        else:
            welcome_message = f"👋 Welcome back {user.first_name}!"
        
        await update.message.reply_text(
            f"{welcome_message}\n"
            "Use the buttons below to navigate.",
            reply_markup=main_keyboard()
        )
        
    except Exception as e:
        print(f"Error saving user: {e}")
        import traceback
        traceback.print_exc()  # Print full error trace
        await update.message.reply_text(
            f"👋 Hello {user.first_name}! Welcome to our Telegram bot. "
            "Use the buttons below to navigate.",
            reply_markup=main_keyboard()
        )
    finally:
        db.close()