"""
API Application Entry Point
Run this file to start the REST API server
"""

from src.api.app import create_app
import os
import sys

def main():
    """Main entry point for API server"""
    try:
        # Create the Flask app
        app = create_app()
        
        # Get configuration from environment variables
        host = os.getenv('API_HOST', '0.0.0.0')
        port = int(os.getenv('API_PORT', 5001))
        debug = os.getenv('API_DEBUG', 'True').lower() == 'true'
            
        # Print startup information
        print(f"\n{'='*60}")
        print(f"🚀 Starting IBS Info Chatbot REST API")
        print(f"{'='*60}")
        print(f"📍 Server: http://{host}:{port}")
        print(f"🔧 Debug Mode: {'Enabled' if debug else 'Disabled'}")
        print(f"📚 API Version: v1")
        print(f"🏥 Health Check: http://{host}:{port}/health")
        print(f"📖 API Root: http://{host}:{port}/api")
        print(f"{'='*60}")
        print(f"\n📋 Available Endpoints:")
        print(f"   Auth:      /api/v1/auth/login")
        print(f"   Users:     /api/v1/users")
        print(f"   Admins:    /api/v1/admins")
        print(f"   Chats:     /api/v1/chats")
        print(f"   Dashboard: /api/v1/dashboard/stats")
        print(f"   Settings:  /api/v1/settings/categories")
        print(f"              /api/v1/settings/faqs")
        print(f"{'='*60}")
        print(f"\n✨ API Server is ready!")
        print(f"Press Ctrl+C to stop the server\n")
        
        # Run the application
        app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=debug,
            threaded=True
        )
        
    except KeyboardInterrupt:
        print("\n\n⛔ Shutting down API server...")
        print("👋 Goodbye!\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting API server: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()