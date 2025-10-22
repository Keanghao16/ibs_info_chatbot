from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from ...database.connection import SessionLocal
from ...database.models import User, ChatSession, Admin, ChatMessage, AdminRole, SystemSettings, FAQ
from ...services.auth_service import AuthService
from ...services.admin_service import AdminService
from ...services.faq_service import FAQService
from sqlalchemy.orm import joinedload
from .auth import login_required, super_admin_required, any_admin_required

admin_bp = Blueprint('admin', __name__)
admin_service = AdminService()

@admin_bp.route('/dashboard')
@any_admin_required
def dashboard():
    db = SessionLocal()
    try:
        users = admin_service.get_all_users(db)
        chats = admin_service.get_all_chat_sessions(db)
        
        current_admin_id = session['admin_info']['id']
        current_admin = db.query(Admin).filter(Admin.id == current_admin_id).first()
        
        if session['admin_info']['role'] == 'admin':
            admin_chats = admin_service.get_admin_chat_sessions(db, current_admin_id)
            return render_template('dashboard/dashboard.html', 
                                 users=users, 
                                 chats=chats, 
                                 admin_chats=admin_chats,
                                 current_admin=current_admin)
        
        return render_template('dashboard/dashboard.html', users=users, chats=chats)
    finally:
        db.close()

@admin_bp.route('/chat-management')
@any_admin_required
def chat_management():
    """Chat management interface for admins to communicate with users"""
    db = SessionLocal()
    try:
        current_admin_id = session['admin_info']['id']
        
        if session['admin_info']['role'] == 'admin':
            active_sessions = admin_service.get_active_chat_sessions(db, current_admin_id)
        else:
            active_sessions = admin_service.get_active_chat_sessions(db)
            
        return render_template('chat/chat_management.html', sessions=active_sessions)
    finally:
        db.close()

@admin_bp.route('/chat/<int:session_id>')
@any_admin_required
def chat_detail(session_id):
    """View specific chat session"""
    db = SessionLocal()
    try:
        current_admin_id = session['admin_info']['id']
        admin_role = session['admin_info']['role']
        
        # Check access
        access_result = admin_service.check_chat_access(db, session_id, current_admin_id, admin_role)
        
        if not access_result['success']:
            flash(access_result['message'], 'error')
            return redirect(url_for('admin.chat_management'))
        
        chat_session = access_result['session']
        
        # Get messages for this session
        messages = admin_service.get_chat_messages(db, chat_session.user_id)
        
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
        admin_role = session['admin_info']['role']
        
        result = admin_service.send_chat_message(
            db=db,
            session_id=session_id,
            admin_id=current_admin_id,
            message_text=message_text,
            admin_role=admin_role
        )
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error sending message: {e}")
        return jsonify({'success': False, 'message': str(e)})
    finally:
        db.close()

@admin_bp.route('/admin/users')
@any_admin_required
def users():
    db = SessionLocal()
    try:
        users = admin_service.get_all_users(db)
        return render_template('user/users.html', users=users)
    finally:
        db.close()

@admin_bp.route('/manage-admins')
@super_admin_required
def manage_admins():
    db = SessionLocal()
    try:
        admins = admin_service.get_all_admins(db)
        return render_template('admin/manage_admins.html', admins=admins)
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
        current_admin_id = session['admin_info']['id']
        result = admin_service.toggle_admin_status(db, admin_id, current_admin_id)
        return jsonify(result)
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
        result = admin_service.toggle_admin_availability(db, current_admin_id)
        
        if result['success']:
            # Update session
            session['admin_info']['is_available'] = result['is_available']
        
        return jsonify(result)
    finally:
        db.close()

@admin_bp.route('/admin/dashboard-stats')
@any_admin_required
def dashboard_stats():
    """API endpoint for dashboard statistics"""
    db = SessionLocal()
    try:
        admin_id = session['admin_info']['id'] if session['admin_info']['role'] == 'admin' else None
        admin_role = session['admin_info']['role']
        
        result = admin_service.get_dashboard_stats(db, admin_id, admin_role)
        return jsonify(result)
    finally:
        db.close()

@admin_bp.route('/admin/close-chat/<int:session_id>', methods=['POST'])
@any_admin_required
def close_chat(session_id):
    """Close a chat session"""
    db = SessionLocal()
    try:
        current_admin_id = session['admin_info']['id']
        admin_role = session['admin_info']['role']
        
        result = admin_service.close_chat_session(db, session_id, current_admin_id, admin_role)
        return jsonify(result)
        
    except Exception as e:
        print(f"Error closing chat: {e}")
        return jsonify({'success': False, 'message': 'Error closing chat session'})
    finally:
        db.close()

@admin_bp.route('/system-settings')
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
        
        # Get all FAQs with their categories
        faqs = db.query(FAQ).options(joinedload(FAQ.faq_category)).order_by(
            FAQ.order_index, 
            FAQ.created_at
        ).all()
        
        # Get categories using the service
        faq_service = FAQService()
        categories = faq_service.get_all_faq_categories(db)
        
        # Convert FAQs to dictionaries
        faqs_dict = [{
            'id': faq.id,
            'question': faq.question,
            'answer': faq.answer,
            'category_id': faq.category_id,
            'category_slug': faq.faq_category.slug if faq.faq_category else None,
            'category_name': faq.faq_category.name if faq.faq_category else 'Unknown',
            'category_icon': faq.faq_category.icon if faq.faq_category else '📁',
            'is_active': faq.is_active,
            'order_index': faq.order_index,
            'created_at': faq.created_at.isoformat() if faq.created_at else None,
            'updated_at': faq.updated_at.isoformat() if faq.updated_at else None
        } for faq in faqs]
        
        # Convert categories to dictionaries
        categories_dict = [{
            'id': cat.id,
            'name': cat.name,
            'slug': cat.slug,
            'description': cat.description,
            'icon': cat.icon,
            'is_active': cat.is_active,
            'order_index': cat.order_index,
            'faq_count': faq_service.get_category_faq_count(db, cat.id)
        } for cat in categories]
        
        return render_template('system_setting/system_settings.html', 
                             settings=settings, 
                             faqs=faqs_dict,
                             categories=categories_dict)
    finally:
        db.close()

# Category CRUD Routes

@admin_bp.route('/admin/save-category', methods=['POST'])
@super_admin_required
def save_category():
    """Create or update FAQ category"""
    db = SessionLocal()
    try:
        faq_service = FAQService()
        category_id = request.form.get('category_id')
        name = request.form.get('name')
        slug = request.form.get('slug')
        description = request.form.get('description')
        icon = request.form.get('icon', '📁')
        is_active = 'is_active' in request.form
        order_index = int(request.form.get('order_index', 0))
        
        if category_id:
            # Update existing category
            try:
                category = faq_service.update_category(
                    db=db,
                    category_id=int(category_id),
                    name=name,
                    slug=slug,
                    description=description,
                    icon=icon,
                    is_active=is_active,
                    order_index=order_index
                )
                if not category:
                    return jsonify({'success': False, 'message': 'Category not found'})
                    
                return jsonify({
                    'success': True,
                    'message': 'Category updated successfully',
                    'category': {
                        'id': category.id,
                        'name': category.name,
                        'slug': category.slug,
                        'description': category.description,
                        'icon': category.icon,
                        'is_active': category.is_active
                    }
                })
            except ValueError as e:
                return jsonify({'success': False, 'message': str(e)})
        else:
            # Create new category
            try:
                category = faq_service.create_category(
                    db=db,
                    name=name,
                    slug=slug,
                    description=description,
                    icon=icon,
                    is_active=is_active,
                    order_index=order_index
                )
                
                return jsonify({
                    'success': True,
                    'message': 'Category created successfully',
                    'category': {
                        'id': category.id,
                        'name': category.name,
                        'slug': category.slug,
                        'description': category.description,
                        'icon': category.icon,
                        'is_active': category.is_active
                    }
                })
            except ValueError as e:
                return jsonify({'success': False, 'message': str(e)})
        
    except Exception as e:
        print(f"Error saving category: {e}")
        return jsonify({'success': False, 'message': 'Error saving category'})
    finally:
        db.close()

@admin_bp.route('/admin/delete-category/<int:category_id>', methods=['DELETE'])
@super_admin_required
def delete_category(category_id):
    """Delete FAQ category"""
    db = SessionLocal()
    try:
        faq_service = FAQService()
        
        try:
            success = faq_service.delete_category(db, category_id)
            
            if not success:
                return jsonify({'success': False, 'message': 'Category not found'})
            
            return jsonify({'success': True, 'message': 'Category deleted successfully'})
        except ValueError as e:
            return jsonify({'success': False, 'message': str(e)})
        
    except Exception as e:
        print(f"Error deleting category: {e}")
        return jsonify({'success': False, 'message': 'Error deleting category'})
    finally:
        db.close()

@admin_bp.route('/admin/api/categories')
@super_admin_required
def get_categories():
    """API endpoint to get all categories"""
    db = SessionLocal()
    try:
        faq_service = FAQService()
        categories = faq_service.get_all_faq_categories(db)
        
        return jsonify({
            'success': True,
            'categories': [{
                'id': cat.id,
                'name': cat.name,
                'slug': cat.slug,
                'description': cat.description,
                'icon': cat.icon,
                'is_active': cat.is_active,
                'order_index': cat.order_index,
                'faq_count': faq_service.get_category_faq_count(db, cat.slug)
            } for cat in categories]
        })
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
        category_id = int(request.form.get('category_id'))  # Changed from category to category_id
        is_active = 'is_active' in request.form
        order_index = int(request.form.get('order_index', 0))
        
        try:
            if faq_id:
                # Update existing FAQ
                faq = faq_service.update_faq(
                    db=db,
                    faq_id=int(faq_id),
                    question=question,
                    answer=answer,
                    category_id=category_id,
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
                    category_id=category_id,
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
                    'category_id': faq.category_id,
                    'is_active': faq.is_active
                }
            })
        except ValueError as e:
            return jsonify({'success': False, 'message': str(e)})
        
    except Exception as e:
        print(f"Error saving FAQ: {e}")
        import traceback
        traceback.print_exc()
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
@admin_bp.route('/admin/api/faqs/<int:category_id>')
@super_admin_required
def get_faqs_by_category(category_id):
    """API endpoint to get FAQs by category ID"""
    db = SessionLocal()
    try:
        faq_service = FAQService()
        faqs = faq_service.get_faqs_by_category(db, category_id)
        
        return jsonify({
            'success': True,
            'faqs': [{
                'id': faq.id,
                'question': faq.question,
                'answer': faq.answer,
                'category_id': faq.category_id,
                'is_active': faq.is_active,
                'order_index': faq.order_index
            } for faq in faqs]
        })
    finally:
        db.close()

@admin_bp.route('/admin-profile/<int:admin_id>')
@super_admin_required
def view_admin_profile(admin_id):
    """View another admin's profile"""
    db = SessionLocal()
    try:
        # Get the admin to view
        admin = db.query(Admin).filter(Admin.id == admin_id).first()
        
        if not admin:
            flash('Admin not found.', 'error')
            return redirect(url_for('admin.manage_admins'))
        
        # Create a temporary admin_info dict for the template
        admin_info = {
            'id': admin.id,
            'telegram_id': admin.telegram_id,
            'telegram_username': admin.telegram_username,
            'telegram_first_name': admin.telegram_first_name,
            'telegram_last_name': admin.telegram_last_name,
            'telegram_photo_url': admin.telegram_photo_url,
            'full_name': admin.full_name,
            'role': admin.role.value if admin.role else 'admin',
            'is_active': admin.is_active,
            'division': admin.division,
            'is_available': admin.is_available,
            'last_login': admin.last_login.strftime('%Y-%m-%d %H:%M:%S') if admin.last_login else None,
            'created_at': admin.created_at.strftime('%Y-%m-%d %H:%M:%S') if admin.created_at else None
        }
        
        # Flag to indicate this is viewing another admin's profile
        is_viewing_other = True
        
        return render_template('admin/admin_profile_view.html', 
                             admin_info=admin_info,
                             is_viewing_other=is_viewing_other)
    finally:
        db.close()