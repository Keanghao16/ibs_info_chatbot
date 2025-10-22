import os
from flask import Flask, redirect, url_for
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
    return redirect(url_for('auth.login'))

if __name__ == "__main__":
    app.run(debug=True)