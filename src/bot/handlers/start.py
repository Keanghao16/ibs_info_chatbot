from telegram import Update
from telegram.ext import ContextTypes
from ..keyboards.inline import main_keyboard, admin_keyboard
from ...utils.bot_api_client import bot_api_client

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    try:
        # Get user profile photo
        photo_url = None
        try:
            photos = await context.bot.get_user_profile_photos(user.id, limit=1)
            if photos.total_count > 0:
                photo = photos.photos[0][-1]
                file = await context.bot.get_file(photo.file_id)
                photo_url = file.file_path
        except Exception as e:
            print(f"Error fetching user photo: {e}")
        
        # Call API to create or get user
        response = bot_api_client.post('/bot/user/create-or-get', {
            'telegram_id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': user.full_name,
            'photo_url': photo_url
        })
        
        if not response.get('success'):
            await update.message.reply_text("⚠️ Service unavailable. Please try again later.")
            return
        
        data = response.get('data', {})
        
        if data.get('is_admin'):
            # User is an admin
            admin = data.get('admin')
            welcome_message = f"👋 Welcome back, {admin.get('full_name')}!\n"
            welcome_message += f"🔐 Role: {admin.get('role', 'admin').replace('_', ' ').title()}\n"
            
            await update.message.reply_text(
                welcome_message + "\nUse the admin panel to manage the system.",
                reply_markup=admin_keyboard()
            )
        else:
            # Regular user
            user_data = data.get('user', {})
            welcome_message = f"👋 Welcome {user.first_name}!"
            
            await update.message.reply_text(
                f"{welcome_message}\nUse the buttons below to navigate.",
                reply_markup=main_keyboard()
            )
            
    except Exception as e:
        print(f"Error in start handler: {e}")
        await update.message.reply_text(
            f"👋 Hello {user.first_name}! Welcome to our Telegram bot.\n"
            "Use the buttons below to navigate.",
            reply_markup=main_keyboard()
        )