"""
Unified Startup Script
Run all services (Web, API, Bot) simultaneously
"""

import subprocess
import sys
import os
from threading import Thread

def run_web():
    """Run web application"""
    subprocess.run([sys.executable, 'run_web.py'])

def run_api():
    """Run REST API"""
    subprocess.run([sys.executable, 'run_api.py'])

def run_bot():
    """Run Telegram bot"""
    subprocess.run([sys.executable, 'run_bot.py'])

if __name__ == "__main__":
    print(f"\n{'='*80}")
    print(f"🚀 Starting All IBS Info Chatbot Services")
    print(f"{'='*80}")
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("❌ ERROR: .env file not found!")
        print("Please copy .env.example to .env and configure it.\n")
        exit(1)
    
    # Start all services in separate threads
    web_thread = Thread(target=run_web, daemon=True)
    api_thread = Thread(target=run_api, daemon=True)
    bot_thread = Thread(target=run_bot, daemon=True)
    
    print("🌐 Starting Web Application...")
    web_thread.start()
    
    print("📡 Starting REST API...")
    api_thread.start()
    
    print("🤖 Starting Telegram Bot...")
    bot_thread.start()
    
    print(f"\n{'='*80}")
    print("✅ All services started successfully!")
    print(f"{'='*80}")
    print("📍 Web App:  http://localhost:5000")
    print("📍 REST API: http://localhost:5001")
    print("📍 Telegram: @digitalguybot")
    print(f"{'='*80}\n")
    print("Press Ctrl+C to stop all services...\n")
    
    try:
        # Keep main thread alive
        web_thread.join()
        api_thread.join()
        bot_thread.join()
    except KeyboardInterrupt:
        print("\n\n⛔ Stopping all services...")
        print("👋 Goodbye!\n")
        sys.exit(0)