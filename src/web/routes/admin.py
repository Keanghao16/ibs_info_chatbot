from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from ...database.connection import SessionLocal
from ...database.models import User, ChatSession, Admin, ChatMessage, AdminRole, SystemSettings, FAQ
from ...services.auth_service import AuthService
from ...services.faq_service import FAQService
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
@super_admin_required
def manage_admins():
    db = SessionLocal()
    try:
        admins = db.query(Admin).all()
        return render_template('manage_admins.html', admins=admins)
    finally:
        db.close()

@admin_bp.route('/admin/create-admin-telegram', methods=['POST'])
@super_admin_required
def create_admin_telegram():
    """Create new admin using Telegram ID"""
    db = SessionLocal()
    try:
        auth_service = AuthService()
        
        telegram_id = request.form.get('telegram_id')
        full_name = request.form.get('full_name')
        role = request.form.get('role', 'admin')
        division = request.form.get('division')
        
        result = auth_service.create_admin_telegram(
            db=db,
            telegram_id=telegram_id,
            full_name=full_name,
            role=role
        )
        
        if result['success']:
            # Update division if provided and role is admin
            if role == 'admin' and division:
                new_admin = db.query(Admin).filter(Admin.telegram_id == telegram_id).first()
                new_admin.division = division
                db.commit()
            
            flash('Admin created successfully!', 'success')
        else:
            flash(result['message'], 'error')
            
    except Exception as e:
        print(f"Error creating admin: {e}")
        flash('Error creating admin account.', 'error')
    finally:
        db.close()
    
    return redirect(url_for('admin.manage_admins'))

@admin_bp.route('/admin/toggle-admin-status/<int:admin_id>', methods=['POST'])
@super_admin_required
def toggle_admin_status(admin_id):
    """Toggle admin active status"""
    db = SessionLocal()
    try:
        admin = db.query(Admin).filter(Admin.id == admin_id).first()
        
        if not admin:
            return jsonify({'success': False, 'message': 'Admin not found'})
        
        # Don't allow deactivating yourself
        if admin.id == session['admin_info']['id']:
            return jsonify({'success': False, 'message': 'You cannot deactivate your own account'})
        
        admin.is_active = not admin.is_active
        db.commit()
        
        status = "activated" if admin.is_active else "deactivated"
        return jsonify({'success': True, 'message': f'Admin {status} successfully'})
        
    except Exception as e:
        print(f"Error toggling admin status: {e}")
        return jsonify({'success': False, 'message': 'Error updating admin status'})
    finally:
        db.close()

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

@admin_bp.route('/admin/close-chat/<int:session_id>', methods=['POST'])
@any_admin_required
def close_chat(session_id):
    """Close a chat session"""
    db = SessionLocal()
    try:
        from ...database.models import SessionStatus
        from datetime import datetime
        
        chat_session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        
        if not chat_session:
            return jsonify({'success': False, 'message': 'Chat session not found'})
        
        # Check if admin has access to this chat
        current_admin_id = session['admin_info']['id']
        if (session['admin_info']['role'] == 'admin' and 
            chat_session.admin_id != current_admin_id):
            return jsonify({'success': False, 'message': 'Access denied'})
        
        # Close the session
        chat_session.status = SessionStatus.closed
        chat_session.end_time = datetime.now()
        db.commit()
        
        return jsonify({'success': True, 'message': 'Chat session closed successfully'})
        
    except Exception as e:
        print(f"Error closing chat: {e}")
        return jsonify({'success': False, 'message': 'Error closing chat session'})
    finally:
        db.close()

@admin_bp.route('/admin/system-settings')
@super_admin_required
def system_settings():
    """System settings page"""
    db = SessionLocal()
    try:
        settings = db.query(SystemSettings).first()
        if not settings:
            settings = SystemSettings()
            db.add(settings)
            db.commit()
            db.refresh(settings)
        
        # Get all FAQs (both active and inactive for admin view)
        faqs = db.query(FAQ).order_by(FAQ.category, FAQ.order_index, FAQ.created_at).all()
        
        # Get categories
        faq_service = FAQService()
        categories = faq_service.get_all_categories(db)
        
        # Convert FAQs to dictionaries for JSON serialization in template
        faqs_dict = [{
            'id': faq.id,
            'question': faq.question,
            'answer': faq.answer,
            'category': faq.category,
            'is_active': faq.is_active,
            'order_index': faq.order_index,
            'created_at': faq.created_at.isoformat() if faq.created_at else None,
            'updated_at': faq.updated_at.isoformat() if faq.updated_at else None
        } for faq in faqs]
        
        return render_template('system_settings.html', 
                             settings=settings, 
                             faqs=faqs_dict,
                             categories=categories)
    finally:
        db.close()

@admin_bp.route('/admin/save-general-settings', methods=['POST'])
@super_admin_required
def save_general_settings():
    """Save general system settings"""
    db = SessionLocal()
    try:
        settings = db.query(SystemSettings).first()
        if not settings:
            settings = SystemSettings()
            db.add(settings)
        
        settings.system_name = request.form.get('system_name')
        settings.welcome_message = request.form.get('welcome_message')
        settings.support_email = request.form.get('support_email')
        settings.max_chat_duration = int(request.form.get('max_chat_duration', 60))
        settings.auto_assign_chats = 'auto_assign_chats' in request.form
        settings.maintenance_mode = 'maintenance_mode' in request.form
        
        db.commit()
        flash('General settings saved successfully!', 'success')
    except Exception as e:
        print(f"Error saving settings: {e}")
        flash('Error saving settings.', 'error')
    finally:
        db.close()
    
    return redirect(url_for('admin.system_settings'))

@admin_bp.route('/admin/save-bot-settings', methods=['POST'])
@super_admin_required
def save_bot_settings():
    """Save bot configuration settings"""
    db = SessionLocal()
    try:
        settings = db.query(SystemSettings).first()
        if not settings:
            settings = SystemSettings()
            db.add(settings)
        
        settings.response_timeout = int(request.form.get('response_timeout', 30))
        settings.offline_message = request.form.get('offline_message')
        settings.enable_file_uploads = 'enable_file_uploads' in request.form
        settings.enable_typing_indicator = 'enable_typing_indicator' in request.form
        
        db.commit()
        flash('Bot settings saved successfully!', 'success')
    except Exception as e:
        print(f"Error saving bot settings: {e}")
        flash('Error saving bot settings.', 'error')
    finally:
        db.close()
    
    return redirect(url_for('admin.system_settings'))

@admin_bp.route('/admin/save-notification-settings', methods=['POST'])
@super_admin_required
def save_notification_settings():
    """Save notification settings"""
    db = SessionLocal()
    try:
        settings = db.query(SystemSettings).first()
        if not settings:
            settings = SystemSettings()
            db.add(settings)
        
        settings.email_notifications = 'email_notifications' in request.form
        settings.notify_new_user = 'notify_new_user' in request.form
        settings.notify_new_chat = 'notify_new_chat' in request.form
        settings.notify_unassigned_chat = 'notify_unassigned_chat' in request.form
        settings.notification_email = request.form.get('notification_email')
        
        db.commit()
        flash('Notification settings saved successfully!', 'success')
    except Exception as e:
        print(f"Error saving notification settings: {e}")
        flash('Error saving notification settings.', 'error')
    finally:
        db.close()
    
    return redirect(url_for('admin.system_settings'))

@admin_bp.route('/admin/save-faq', methods=['POST'])
@super_admin_required
def save_faq():
    """Save or update FAQ"""
    db = SessionLocal()
    try:
        faq_service = FAQService()
        faq_id = request.form.get('faq_id')
        question = request.form.get('question')
        answer = request.form.get('answer')
        category = request.form.get('category', 'general')
        is_active = 'is_active' in request.form
        order_index = int(request.form.get('order_index', 0))
        
        if faq_id:
            # Update existing FAQ
            faq = faq_service.update_faq(
                db=db,
                faq_id=int(faq_id),
                question=question,
                answer=answer,
                category=category,
                is_active=is_active,
                order_index=order_index
            )
            if not faq:
                return jsonify({'success': False, 'message': 'FAQ not found'})
        else:
            # Create new FAQ
            faq = faq_service.create_faq(
                db=db,
                question=question,
                answer=answer,
                category=category,
                is_active=is_active,
                order_index=order_index
            )
        
        return jsonify({
            'success': True, 
            'message': 'FAQ saved successfully',
            'faq': {
                'id': faq.id,
                'question': faq.question,
                'answer': faq.answer,
                'category': faq.category,
                'is_active': faq.is_active
            }
        })
        
    except Exception as e:
        print(f"Error saving FAQ: {e}")
        return jsonify({'success': False, 'message': 'Error saving FAQ'})
    finally:
        db.close()

@admin_bp.route('/admin/delete-faq/<int:faq_id>', methods=['DELETE'])
@super_admin_required
def delete_faq(faq_id):
    """Delete FAQ"""
    db = SessionLocal()
    try:
        faq_service = FAQService()
        success = faq_service.delete_faq(db, faq_id)
        
        if not success:
            return jsonify({'success': False, 'message': 'FAQ not found'})
        
        return jsonify({'success': True, 'message': 'FAQ deleted successfully'})
        
    except Exception as e:
        print(f"Error deleting FAQ: {e}")
        return jsonify({'success': False, 'message': 'Error deleting FAQ'})
    finally:
        db.close()

# Add new route to get FAQs by category (API endpoint)
@admin_bp.route('/admin/api/faqs/<category>')
@super_admin_required
def get_faqs_by_category(category):
    """API endpoint to get FAQs by category"""
    db = SessionLocal()
    try:
        faq_service = FAQService()
        faqs = faq_service.get_faqs_by_category(db, category)
        
        return jsonify({
            'success': True,
            'faqs': [{
                'id': faq.id,
                'question': faq.question,
                'answer': faq.answer,
                'category': faq.category,
                'is_active': faq.is_active,
                'order_index': faq.order_index
            } for faq in faqs]
        })
    finally:
        db.close()