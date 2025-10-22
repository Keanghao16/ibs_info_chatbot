import os
from flask import Flask, redirect, url_for, session
from ..utils.config import Config

ADMIN_PREFIX = os.getenv('ADMIN_URL_PREFIX', '/portal/admin')

from .routes.auth import auth_bp
from .routes.admin import admin_bp
from .routes.users import users_bp
from .routes.chats import chats_bp

app = Flask(__name__)

# Load configuration
app.config.from_object(Config)

# Set secret key explicitly
app.secret_key = Config.SECRET_KEY

# Register blueprints with /portal/admin prefix
app.register_blueprint(auth_bp, url_prefix=ADMIN_PREFIX)
app.register_blueprint(admin_bp, url_prefix=ADMIN_PREFIX)
app.register_blueprint(users_bp, url_prefix=ADMIN_PREFIX)
app.register_blueprint(chats_bp, url_prefix=ADMIN_PREFIX)

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
        return redirect(url_for('admin.dashboard'))
    else:
        # User is not logged in, redirect to login
        return redirect(url_for('auth.login'))

if __name__ == "__main__":
    app.run(debug=True)