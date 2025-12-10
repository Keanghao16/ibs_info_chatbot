# ============================================================================
# FILE: src/bot/keyboards/inline.py
# UPDATED - More intuitive labels
# ============================================================================

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_keyboard():
    keyboard = [
        [InlineKeyboardButton("💬 Chat with Agent", callback_data='start_chat')],
        [InlineKeyboardButton("📚 Browse FAQs", callback_data='faq')],
    ]
    return InlineKeyboardMarkup(keyboard)

def admin_keyboard():
    keyboard = [
        [InlineKeyboardButton("👤 Manage Users", callback_data='manage_users')],
        [InlineKeyboardButton("📜 View Chat History", callback_data='view_chat_history')],
        [InlineKeyboardButton("📚 Browse FAQs", callback_data='faq')],
    ]
    return InlineKeyboardMarkup(keyboard)