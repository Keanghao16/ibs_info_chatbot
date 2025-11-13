"""
API Application Entry Point
Run this file to start the REST API server
"""

from src.api.app import create_app
import os

if __name__ == '__main__':
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
    print(f"{'='*60}\n")
    
    # Run the application
    app.run(
        host=host,
        port=port,
        debug=debug
    )