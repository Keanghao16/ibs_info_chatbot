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
        # Check if user is logged in by checking session
        if 'admin_token' in session and 'admin_info' in session:
            # User is logged in, redirect to dashboard
            return redirect(url_for('dashboard.dashboard'))
        else:
            # User is not logged in, redirect to login
            return redirect(url_for('auth.login'))
    
    return app

# Create app instance for imports
app = create_app()

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)