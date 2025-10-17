from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from ...database.connection import SessionLocal
from ...database.models import User, ChatSession, Admin, ChatMessage, AdminRole
from .auth import login_required, super_admin_required, any_admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/dashboard')
@any_admin_required  # Both super_admin and admin can access
def dashboard():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        chats = db.query(ChatSession).all()
        
        # Get current admin info
        current_admin_id = session['admin_info']['id']
        current_admin = db.query(Admin).filter(Admin.id == current_admin_id).first()
        
        # If admin role, show their specific stats
        if session['admin_info']['role'] == 'admin':
            admin_chats = db.query(ChatSession).filter(ChatSession.admin_id == current_admin_id).all()
            return render_template('dashboard.html', 
                                 users=users, 
                                 chats=chats, 
                                 admin_chats=admin_chats,
                                 current_admin=current_admin)
        
        return render_template('dashboard.html', users=users, chats=chats)
    finally:
        db.close()

@admin_bp.route('/admin/chat-management')
@any_admin_required
def chat_management():
    """Chat management interface for admins to communicate with users"""
    db = SessionLocal()
    try:
        current_admin_id = session['admin_info']['id']
        
        if session['admin_info']['role'] == 'admin':
            # Admin sees only their assigned chats
            active_sessions = db.query(ChatSession).filter(
                ChatSession.admin_id == current_admin_id,
                ChatSession.status == 'active'
            ).all()
        else:
            # Super admin sees all active chats
            active_sessions = db.query(ChatSession).filter(
                ChatSession.status == 'active'
            ).all()
            
        return render_template('chat_management.html', sessions=active_sessions)
    finally:
        db.close()

@admin_bp.route('/admin/chat/<int:session_id>')
@any_admin_required
def chat_detail(session_id):
    """View specific chat session"""
    db = SessionLocal()
    try:
        chat_session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        
        if not chat_session:
            flash('Chat session not found.', 'error')
            return redirect(url_for('admin.chat_management'))
        
        # Check if admin has access to this chat
        current_admin_id = session['admin_info']['id']
        if (session['admin_info']['role'] == 'admin' and 
            chat_session.admin_id != current_admin_id):
            flash('Access denied. You can only view your assigned chats.', 'error')
            return redirect(url_for('admin.chat_management'))
        
        # Get messages for this session
        messages = db.query(ChatMessage).filter(
            ChatMessage.user_id == chat_session.user_id
        ).order_by(ChatMessage.timestamp).all()
        
        return render_template('chat_detail.html', 
                             session=chat_session, 
                             messages=messages)
    finally:
        db.close()

@admin_bp.route('/admin/send-message', methods=['POST'])
@any_admin_required
def send_message():
    """Send message to user (for admin communication)"""
    db = SessionLocal()
    try:
        session_id = request.form.get('session_id')
        message_text = request.form.get('message')
        current_admin_id = session['admin_info']['id']
        
        chat_session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        
        if not chat_session:
            return jsonify({'success': False, 'message': 'Session not found'})
        
        # Create message record
        new_message = ChatMessage(
            user_id=chat_session.user_id,
            admin_id=current_admin_id,
            message=message_text,
            is_from_admin=True
        )
        
        db.add(new_message)
        db.commit()
        
        # Here you would integrate with your Telegram bot to send the message
        # send_telegram_message(chat_session.user.telegram_id, message_text)
        
        return jsonify({'success': True, 'message': 'Message sent successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        db.close()

@admin_bp.route('/admin/users')
@any_admin_required
def users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        return render_template('users.html', users=users)
    finally:
        db.close()

@admin_bp.route('/admin/manage-admins')
@super_admin_required  # Only super_admin can manage other admins
def manage_admins():
    db = SessionLocal()
    try:
        admins = db.query(Admin).all()
        return render_template('manage_admins.html', admins=admins)
    finally:
        db.close()

@admin_bp.route('/admin/create-admin', methods=['GET', 'POST'])
@super_admin_required
def create_admin():
    if request.method == 'POST':
        db = SessionLocal()
        try:
            from ...services.auth_service import AuthService
            auth_service = AuthService()
            
            result = auth_service.create_admin(
                db=db,
                email=request.form['email'],
                password=request.form['password'],
                full_name=request.form['full_name']
            )
            
            if result['success']:
                # Update additional fields for admin role
                new_admin = db.query(Admin).filter(Admin.email == request.form['email']).first()
                new_admin.telegram_id = request.form.get('telegram_id')
                new_admin.division = request.form.get('division')
                new_admin.role = AdminRole.admin  # Set as admin (agent)
                db.commit()
                
                flash('Admin created successfully!', 'success')
                return redirect(url_for('admin.manage_admins'))
            else:
                flash(result['message'], 'error')
                
        finally:
            db.close()
    
    return render_template('create_admin.html')

@admin_bp.route('/admin/toggle-availability', methods=['POST'])
@any_admin_required
def toggle_availability():
    """Toggle admin availability for taking new chats"""
    db = SessionLocal()
    try:
        current_admin_id = session['admin_info']['id']
        admin = db.query(Admin).filter(Admin.id == current_admin_id).first()
        
        if admin:
            admin.is_available = not admin.is_available
            db.commit()
            
            status = "available" if admin.is_available else "unavailable"
            return jsonify({'success': True, 'status': status})
        
        return jsonify({'success': False, 'message': 'Admin not found'})
        
    finally:
        db.close()

@admin_bp.route('/admin/dashboard-stats')
@any_admin_required
def dashboard_stats():
    """API endpoint for dashboard statistics"""
    db = SessionLocal()
    try:
        users_count = db.query(User).count()
        chats_count = db.query(ChatSession).count()
        
        # If admin role, get their specific stats
        admin_chats_count = 0
        if session['admin_info']['role'] == 'admin':
            current_admin_id = session['admin_info']['id']
            admin_chats_count = db.query(ChatSession).filter(
                ChatSession.admin_id == current_admin_id
            ).count()
        
        return jsonify({
            'success': True,
            'users': users_count,
            'chats': chats_count,
            'admin_chats': admin_chats_count
        })
    finally:
        db.close()