"""
API Application Factory
Initializes Flask app for REST API with CORS, error handling, and middleware
"""

from flask import Flask, jsonify, request
import os
from ..utils.config import Config

# API Version prefix
API_PREFIX = '/api/v1'

def create_app():
    """
    Create and configure the Flask API application
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    
    # Configure CORS
    from .v1.middleware.cors import configure_cors
    configure_cors(app)
    
    # Register error handlers (using new middleware)
    from .v1.middleware.error_handler import register_error_handlers
    register_error_handlers(app)
    
    # Register blueprints (API routes)
    register_blueprints(app)
    
    # Register request/response handlers
    register_request_handlers(app)
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """API health check endpoint"""
        return jsonify({
            'success': True,
            'message': 'API is running',
            'version': 'v1'
        }), 200
    
    # Root API endpoint
    @app.route('/api')
    def api_root():
        """API root endpoint with documentation links"""
        return jsonify({
            'success': True,
            'message': 'IBS Info Chatbot API',
            'version': 'v1',
            'endpoints': {
                'health': '/health',
                'auth': f'{API_PREFIX}/auth',
                'users': f'{API_PREFIX}/users',
                'admins': f'{API_PREFIX}/admins',
                'chats': f'{API_PREFIX}/chats',
                'dashboard': f'{API_PREFIX}/dashboard',
                'settings': f'{API_PREFIX}/settings'
            }
        }), 200
    
    return app


def register_blueprints(app):
    """
    Register all API blueprints (routes)
    
    Args:
        app: Flask application instance
    """
    # Import blueprints
    from .v1.routes.test_auth import test_auth_bp
    from .v1.routes.test_jwt import test_jwt_bp
    from .v1.routes.auth import auth_api_bp  # ✅ NEW
    
    # Register blueprints
    app.register_blueprint(test_auth_bp, url_prefix=f'{API_PREFIX}')
    app.register_blueprint(test_jwt_bp, url_prefix=f'{API_PREFIX}')
    app.register_blueprint(auth_api_bp, url_prefix=f'{API_PREFIX}')  # ✅ NEW
    
    print("✅ API blueprints registered")


def register_request_handlers(app):
    """
    Register before/after request handlers for logging and response formatting
    
    Args:
        app: Flask application instance
    """
    
    @app.before_request
    def before_request():
        """Log incoming requests"""
        # Skip logging for health check
        if request.path == '/health':
            return
        
        app.logger.info(f"📥 {request.method} {request.path}")
        
        # Log request body for POST/PUT/DELETE
        if request.method in ['POST', 'PUT', 'DELETE'] and request.is_json:
            app.logger.debug(f"Request body: {request.get_json()}")
    
    @app.after_request
    def after_request(response):
        """Add common headers to all responses"""
        # Skip for health check
        if request.path == '/health':
            return response
        
        # Add custom headers
        response.headers['X-API-Version'] = 'v1'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        app.logger.info(f"📤 {request.method} {request.path} - Status: {response.status_code}")
        
        return response
    
    @app.teardown_appcontext
    def teardown_db(exception=None):
        """Close database connections"""
        if exception:
            app.logger.error(f"Teardown exception: {str(exception)}")
    
    print("✅ Request handlers registered")


# Create app instance for imports
app = create_app()

if __name__ == '__main__':
    # Get configuration from environment
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', 5001))
    debug = os.getenv('API_DEBUG', 'True').lower() == 'true'
    
    print(f"\n{'='*60}")
    print(f"🚀 Starting IBS Info Chatbot API")
    print(f"{'='*60}")
    print(f"📍 URL: http://{host}:{port}")
    print(f"🔧 Debug Mode: {debug}")
    print(f"📚 API Version: v1")
    print(f"{'='*60}\n")
    
    app.run(
        host=host,
        port=port,
        debug=debug
    )