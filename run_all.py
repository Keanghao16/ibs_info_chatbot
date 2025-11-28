"""
Run All Services
Starts Web App, REST API, and Telegram Bot simultaneously
"""

import sys
import subprocess
import threading
import time
import signal

# Flag to track if services should continue running
running = True

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    global running
    print("\n\n⛔ Received shutdown signal...")
    running = False
    sys.exit(0)

# Register signal handler
signal.signal(signal.SIGINT, signal_handler)


def run_web():
    """Run web application"""
    try:
        subprocess.run([sys.executable, 'run_web.py'])
    except Exception as e:
        print(f"❌ Web App Error: {e}")


def run_api():
    """Run REST API"""
    try:
        subprocess.run([sys.executable, 'run_api.py'])
    except Exception as e:
        print(f"❌ API Error: {e}")


def run_bot():
    """Run Telegram bot"""
    try:
        subprocess.run([sys.executable, 'run_bot.py'])
    except Exception as e:
        print(f"❌ Bot Error: {e}")


def main():
    """Main entry point"""
    print(f"\n{'='*80}")
    print("🚀 IBS Info Chatbot - Starting All Services")
    print(f"{'='*80}\n")
    
    # Create threads for each service
    web_thread = threading.Thread(target=run_web, name="WebApp", daemon=True)
    api_thread = threading.Thread(target=run_api, name="API", daemon=True)
    bot_thread = threading.Thread(target=run_bot, name="Bot", daemon=True)
    
    # Start all services
    print("🌐 Starting Web Application...")
    web_thread.start()
    time.sleep(2)  # Wait for web to initialize
    
    print("📡 Starting REST API...")
    api_thread.start()
    time.sleep(2)  # Wait for API to initialize
    
    print("🤖 Starting Telegram Bot...")
    bot_thread.start()
    time.sleep(2)  # Wait for bot to initialize
    
    print(f"\n{'='*80}")
    print("✅ All services started successfully!")
    print(f"{'='*80}")
    print("📍 Web App:       http://localhost:5000")
    print("📍 REST API:      http://localhost:5001")
    print("📍 API Health:    http://localhost:5001/health")
    print("📍 Telegram Bot:  @digitalguybot")
    print(f"{'='*80}\n")
    print("💡 Tip: Use Ctrl+C to stop all services")
    print(f"{'='*80}\n")
    
    try:
        # Keep main thread alive
        while running:
            time.sleep(1)
            
            # Check if any thread died
            if not web_thread.is_alive():
                print("⚠️  Web App thread died, restarting...")
                web_thread = threading.Thread(target=run_web, name="WebApp", daemon=True)
                web_thread.start()
            
            if not api_thread.is_alive():
                print("⚠️  API thread died, restarting...")
                api_thread = threading.Thread(target=run_api, name="API", daemon=True)
                api_thread.start()
            
            if not bot_thread.is_alive():
                print("⚠️  Bot thread died, restarting...")
                bot_thread = threading.Thread(target=run_bot, name="Bot", daemon=True)
                bot_thread.start()
                
    except KeyboardInterrupt:
        print("\n\n⛔ Stopping all services...")
        print("👋 Goodbye!\n")
        sys.exit(0)


if __name__ == '__main__':
    main()