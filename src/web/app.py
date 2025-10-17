from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import json
import enum

class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, enum.Enum):
            return obj.value
        return super().default(obj)

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "your_secret_key")

# Set custom JSON encoder
app.json_encoder = EnumEncoder

db = SQLAlchemy(app)

# Import routes after app initialization to avoid circular imports
from .routes import admin, users, chats, auth

app.register_blueprint(auth.auth_bp)
app.register_blueprint(admin.admin_bp)
app.register_blueprint(users.users_bp)
app.register_blueprint(chats.chats_bp)

@app.route('/')
def index():
    return redirect(url_for('auth.login'))

if __name__ == "__main__":
    app.run(debug=True)