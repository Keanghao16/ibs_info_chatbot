from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_keyboard():
    keyboard = [
        [InlineKeyboardButton("💬 Start Chat", callback_data='start_chat')],
        [InlineKeyboardButton("📚 FAQ", callback_data='faq')],
    ]
    return InlineKeyboardMarkup(keyboard)

def admin_keyboard():
    keyboard = [
        [InlineKeyboardButton("👤 Manage Users", callback_data='manage_users')],
        [InlineKeyboardButton("📜 View Chat History", callback_data='view_chat_history')],
    ]
    return InlineKeyboardMarkup(keyboard)