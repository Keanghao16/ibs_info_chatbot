import os
from flask import Flask, redirect, url_for, session
from ..utils import Config
from .websocket_manager import socketio

ADMIN_PREFIX = '/portal/admin'

# Import all blueprints from routes package
from .routes import (
    auth_bp,
    admin_bp,
    users_bp,
    chats_bp,
    dashboard_bp,
    system_settings_bp
)

def create_app():
    app = Flask(__name__)
    # Load configuration
    app.config.from_object(Config)

    # Set secret key explicitly
    app.secret_key = Config.SECRET_KEY

    # Initialize SocketIO
    socketio.init_app(app)

    #  Add hasattr to Jinja2 globals
    app.jinja_env.globals['hasattr'] = hasattr

    #  Add custom template filters
    @app.template_filter('safe_datetime')
    def safe_datetime_filter(value, format='%Y-%m-%d %H:%M'):
        """Safely format datetime, handling both string and datetime objects"""
        if not value:
            return 'Never'
        
        try:
            if isinstance(value, str):
                # Try to parse ISO format
                from datetime import datetime
                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                return dt.strftime(format)
            elif hasattr(value, 'strftime'):
                # It's already a datetime object
                return value.strftime(format)
            else:
                return str(value)
        except:
            return str(value) if value else 'Never'
    
    @app.template_filter('safe_date')
    def safe_date_filter(value):
        """Safely format date only"""
        return safe_datetime_filter(value, '%Y-%m-%d')

    # Register blueprints with /portal/admin prefix
    app.register_blueprint(auth_bp, url_prefix=ADMIN_PREFIX)
    app.register_blueprint(admin_bp, url_prefix=ADMIN_PREFIX)
    app.register_blueprint(users_bp, url_prefix=ADMIN_PREFIX)
    app.register_blueprint(chats_bp, url_prefix=ADMIN_PREFIX)
    app.register_blueprint(dashboard_bp, url_prefix=ADMIN_PREFIX)
    app.register_blueprint(system_settings_bp, url_prefix=ADMIN_PREFIX)

    @app.route('/')
    def index():
        """Root redirect - goes to portal admin"""
        return redirect(url_for('portal_admin_index'))

    @app.route('/portal/admin')
    def portal_admin_index():
        """
        Portal admin index route
        Redirects to dashboard if logged in, otherwise to login
        """
        #  UPDATED: Check for API-based session variables
        if 'access_token' in session and 'admin' in session:
            # User is logged in via API, redirect to dashboard
            return redirect(url_for('dashboard.index'))
        else:
            # User is not logged in, redirect to login
            return redirect(url_for('auth.login'))

    @app.after_request
    def add_security_headers(response):
        """Add security headers - CSP temporarily disabled for testing"""
        # ❌ Temporarily disable CSP
        # response.headers['Content-Security-Policy'] = csp
        
        # Bypass ngrok warning
        response.headers['ngrok-skip-browser-warning'] = 'true'
        
        return response

    return app

# Create app instance for imports
app = create_app()

if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv('WEB_HOST', '0.0.0.0')
    port = int(os.getenv('WEB_PORT', 5000))
    debug = os.getenv('WEB_DEBUG', 'True').lower() == 'true'
    
    print(f"\n{'='*60}")
    print(f"🌐 Starting IBS Info Chatbot Web Application")
    print(f"{'='*60}")
    print(f"📍 URL: https://chatbot.ibs.local")
    print(f"🔧 Debug Mode: {debug}")
    print(f"📊 Internal Port: {port}")
    print(f"{'='*60}\n")
    
    socketio.run(app, host=host, port=port, debug=debug)