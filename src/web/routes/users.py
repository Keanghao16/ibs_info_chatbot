from flask import Blueprint, render_template, request, redirect, url_for
from ...database.connection import SessionLocal
from ...database.models import User

users_bp = Blueprint('users', __name__)

@users_bp.route('/users')
def list_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        return render_template('user/users.html', users=users)
    finally:
        db.close()

@users_bp.route('/users/delete/<int:user_id>', methods=['POST'])
def remove_user(user_id):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            db.delete(user)
            db.commit()
        return redirect(url_for('users.list_users'))
    finally:
        db.close()