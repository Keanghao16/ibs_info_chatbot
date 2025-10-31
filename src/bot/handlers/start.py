from telegram import Update
from telegram.ext import ContextTypes
from ..keyboards.inline import main_keyboard, admin_keyboard
from ...database.connection import SessionLocal
from ...services import UserService  
from datetime import datetime

user_service = UserService()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    db = SessionLocal()
    try:
        # Get user profile photos
        photo_url = None
        try:
            photos = await context.bot.get_user_profile_photos(user.id, limit=1)
            if photos.total_count > 0:
                photo = photos.photos[0][-1]
                file = await context.bot.get_file(photo.file_id)
                photo_url = file.file_path
        except Exception as e:
            print(f"Error fetching user photo: {e}")
        
        # Check if user is admin or regular user
        result = user_service.get_user_or_admin_by_telegram_id(db, str(user.id))  # ✅ Use service
        
        if result and result['type'] == "admin":
            # User is an admin - show admin interface
            record = result['data']
            welcome_message = f"👋 Welcome back, {record.full_name}!\n"
            welcome_message += f"🔐 Role: {record.role.value.replace('_', ' ').title()}\n"
            if record.division:
                welcome_message += f"📁 Division: {record.division}\n"
            
            await update.message.reply_text(
                welcome_message + "\nUse the admin panel to manage the system.",
                reply_markup=admin_keyboard()  # Show admin keyboard
            )
            
            # Update last login
            record.last_login = datetime.now()
            db.commit()
            
        else:
            # Create or get regular user (won't create if already admin)
            create_result = user_service.create_user_if_not_admin(  # ✅ Use service
                db=db,
                telegram_id=str(user.id),
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                full_name=user.full_name,
                photo_url=photo_url
            )
            
            if create_result['success']:
                created_user = create_result['user']
                # Check if newly created
                is_new_user = created_user.created_at and (
                    datetime.now() - created_user.created_at.replace(tzinfo=None)
                ).total_seconds() < 5
                
                if is_new_user:
                    welcome_message = f"👋 Welcome {user.first_name}! You've been registered successfully."
                else:
                    welcome_message = f"👋 Welcome back {user.first_name}!"
                
                await update.message.reply_text(
                    f"{welcome_message}\n"
                    "Use the buttons below to navigate.",
                    reply_markup=main_keyboard()
                )
            else:
                # This shouldn't happen, but just in case
                await update.message.reply_text(
                    "⚠️ Unable to create user profile. Please contact support."
                )
        
    except Exception as e:
        print(f"Error in start handler: {e}")
        import traceback
        traceback.print_exc()
        await update.message.reply_text(
            f"👋 Hello {user.first_name}! Welcome to our Telegram bot.\n"
            "Use the buttons below to navigate.",
            reply_markup=main_keyboard()
        )
    finally:
        db.close()