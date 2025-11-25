"""
Web Application Entry Point
Run this file to start the web application with admin dashboard
"""

from src.web.app import create_app
from src.web.websocket_manager import socketio
import os

if __name__ == "__main__":
    # Create the Flask app
    app = create_app()
    
    # Get configuration from environment variables
    host = os.getenv('WEB_HOST', '127.0.0.1')
    port = int(os.getenv('WEB_PORT', 5000))
    debug = os.getenv('WEB_DEBUG', 'True').lower() == 'true'


    # Print startup information
    print(f"\n{'='*60}")
    print(f"🌐 Starting IBS Info Chatbot Web Application")
    print(f"{'='*60}")
    print(f"📍 Server: http://{host}:{port}")
    print(f"🔧 Debug Mode: {'Enabled' if debug else 'Disabled'}")
    print(f"🔐 Admin Panel: http://{host}:{port}/portal/admin")
    print(f"💬 WebSocket: Enabled")
    print(f"{'='*60}\n")
    
    # Use socketio.run instead of app.run for WebSocket support
    socketio.run(
        app, 
        host=host, 
        port=port, 
        debug=debug,
    )