import os
from flask import Flask, redirect, url_for, session
from ..utils import Config
from .websocket_manager import socketio
from datetime import datetime
import pytz  # Add this import

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

    # Add hasattr to Jinja2 globals
    app.jinja_env.globals['hasattr'] = hasattr

    # UPDATED FILTER for Cambodia timezone - Database already in UTC+7
    @app.template_filter('cambodia_time')
    def cambodia_time_filter(dt):
        """Format datetime that's already in Cambodia time (UTC+7)"""
        if dt is None:
            return 'N/A'
        
        # If input is a string, parse it first
        if isinstance(dt, str):
            try:
                # Parse ISO format string: "2025-12-10T13:50:12" or "2025-12-10T13:50:12.123456"
                dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                return dt  # Return original string if parsing fails

        # Database already stores Cambodia time (UTC+7), just format it
        # Format: Dec 10, 2025 14:30
        return dt.strftime('%b %d, %Y %H:%M')
    
    @app.template_filter('cambodia_time_full')
    def cambodia_time_full_filter(dt):
        """Format datetime with seconds - already in Cambodia time"""
        if dt is None:
            return 'N/A'
        
        # If input is a string, parse it first
        if isinstance(dt, str):
            try:
                dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                return dt
    
        # Database already stores Cambodia time (UTC+7), just format it
        # Format: 2025-12-10 14:30:45
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    # Add custom template filters (your existing filters)
    @app.template_filter('safe_datetime')
    def safe_datetime_filter(value):
        """Safely format datetime objects"""
        if value is None:
            return 'N/A'
        try:
            if isinstance(value, str):
                from dateutil import parser
                value = parser.parse(value)
            return value.strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            return str(value)
    
    @app.template_filter('safe_date')
    def safe_date_filter(value):
        """Safely format date objects"""
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