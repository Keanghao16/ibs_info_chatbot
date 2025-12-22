"""
Telegram Bot Entry Point
Run this file to start the Telegram bot
"""

from src.bot.main import main
import os

if __name__ == "__main__":
    bot_token = os.getenv('BOT_TOKEN')
    bot_username = os.getenv('BOT_USERNAME', 'Unknown')
    
    # Print startup information
    print(f"\n{'='*60}")
    print(f"🤖 Starting IBS Info Chatbot - Telegram Bot")
    print(f"{'='*60}")
    print(f"📱 Bot Username: @{bot_username}")
    print(f"🔌 Connection: Telegram Polling")
    print(f" Bot Token: {'Configured' if bot_token else '❌ Missing'}")
    print(f"{'='*60}\n")
    
    if not bot_token:
        print("❌ ERROR: BOT_TOKEN not found in .env file!")
        print("Please add your bot token to the .env file.\n")
        exit(1)
    
    # Start the bot
    main()