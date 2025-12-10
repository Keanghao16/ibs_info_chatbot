from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from ...utils.apiClient import api_client
from ..auth_decorators import any_admin_required, super_admin_required

system_settings_bp = Blueprint('system_settings', __name__)

@system_settings_bp.route('/system-settings')
@super_admin_required
def index():
    """System settings page - uses API for all data"""
    try:
        # Get categories from API
        categories_response = api_client.get('/api/v1/settings/categories')
        
        if not categories_response.get('success'):
            flash('Failed to load categories from API', 'error')
            categories = []
        else:
            categories = categories_response.get('data', [])
        
        # Get FAQs from API
        faqs_response = api_client.get('/api/v1/settings/faqs')
        
        if not faqs_response.get('success'):
            flash('Failed to load FAQs from API', 'error')
            faqs = []
        else:
            faqs = faqs_response.get('data', [])
        
        # Get system settings (still direct DB - no API endpoint yet)
        from ...database.connection import SessionLocal
        from ...services import SystemSettingService
        
        db = SessionLocal()
        try:
            system_setting_service = SystemSettingService()
            settings = system_setting_service.get_settings(db)
            
            return render_template('system_setting/index.html', 
                                 settings=settings, 
                                 faqs=faqs,
                                 categories=categories)
        finally:
            db.close()
            
    except Exception as e:
        flash(f'Error loading system settings: {str(e)}', 'error')
        return render_template('system_setting/index.html', 
                             settings=None, 
                             faqs=[],
                             categories=[])

@system_settings_bp.route('/system-settings/save-general', methods=['POST'])
@super_admin_required
def save_general_settings():
    """Save general system settings (still using direct DB access - no API endpoint yet)"""
    from ...database.connection import SessionLocal
    from ...services import SystemSettingService
    
    db = SessionLocal()
    try:
        system_setting_service = SystemSettingService()
        settings_data = {
            'system_name': request.form.get('system_name'),
            'welcome_message': request.form.get('welcome_message'),
            'support_email': request.form.get('support_email'),
            'max_chat_duration': request.form.get('max_chat_duration', 60),
            'auto_assign_chats': 'auto_assign_chats' in request.form,
            'maintenance_mode': 'maintenance_mode' in request.form
        }
        
        result = system_setting_service.update_general_settings(db, settings_data)
        
        if result['success']:
            flash(result['message'], 'success')
        else:
            flash(result['message'], 'error')
            
    except Exception as e:
        print(f"Error saving settings: {e}")
        flash('Error saving settings.', 'error')
    finally:
        db.close()
    
    return redirect(url_for('system_settings.index'))

@system_settings_bp.route('/system-settings/save-bot', methods=['POST'])
@super_admin_required
def save_bot_settings():
    """Save bot configuration settings (still using direct DB access - no API endpoint yet)"""
    from ...database.connection import SessionLocal
    from ...services import SystemSettingService
    
    db = SessionLocal()
    try:
        system_setting_service = SystemSettingService()
        settings_data = {
            'response_timeout': request.form.get('response_timeout', 30),
            'max_concurrent_chats': request.form.get('max_concurrent_chats', 5),
            'enable_ai_assistant': 'enable_ai_assistant' in request.form,
            'ai_model': request.form.get('ai_model', 'gpt-3.5-turbo')
        }
        
        result = system_setting_service.update_bot_settings(db, settings_data)
        
        if result['success']:
            flash(result['message'], 'success')
        else:
            flash(result['message'], 'error')
            
    except Exception as e:
        print(f"Error saving bot settings: {e}")
        flash('Error saving bot settings.', 'error')
    finally:
        db.close()
    
    return redirect(url_for('system_settings.index'))

@system_settings_bp.route('/system-settings/save-notifications', methods=['POST'])
@super_admin_required
def save_notification_settings():
    """Save notification settings (still using direct DB access - no API endpoint yet)"""
    from ...database.connection import SessionLocal
    from ...services import SystemSettingService
    
    db = SessionLocal()
    try:
        system_setting_service = SystemSettingService()
        settings_data = {
            'email_notifications': 'email_notifications' in request.form,
            'sms_notifications': 'sms_notifications' in request.form,
            'push_notifications': 'push_notifications' in request.form,
            'notification_frequency': request.form.get('notification_frequency', 'immediate')
        }
        
        result = system_setting_service.update_notification_settings(db, settings_data)
        
        if result['success']:
            flash(result['message'], 'success')
        else:
            flash(result['message'], 'error')
            
    except Exception as e:
        print(f"Error saving notification settings: {e}")
        flash('Error saving notification settings.', 'error')
    finally:
        db.close()
    
    return redirect(url_for('system_settings.index'))

# --------------------------------------------------------------------------
# Category Management Routes - Using API
# --------------------------------------------------------------------------

@system_settings_bp.route('/system-settings/save-category', methods=['POST'])
@super_admin_required
def save_category():
    """Create or update FAQ category using API"""
    try:
        category_id = request.form.get('category_id')
        category_data = {
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'icon': request.form.get('icon', '📁'),
            'is_active': 'is_active' in request.form,
            'order_index': int(request.form.get('order_index', 0))
        }
        
        if category_id:
            # Update existing category
            response = api_client.put(f'/api/v1/settings/categories/{category_id}', category_data)
        else:
            # Create new category
            response = api_client.post('/api/v1/settings/categories', category_data)
        
        if response.get('success'):
            return jsonify({
                'success': True,
                'message': response.get('message', 'Category saved successfully'),
                'category': response.get('data', {})
            })
        else:
            return jsonify({
                'success': False,
                'message': response.get('message', 'Failed to save category')
            })
            
    except Exception as e:
        print(f"Error saving category: {e}")
        return jsonify({'success': False, 'message': 'Error saving category'})

@system_settings_bp.route('/system-settings/delete-category/<int:category_id>', methods=['DELETE'])
@super_admin_required
def delete_category(category_id):
    """Delete FAQ category using API"""
    try:
        response = api_client.delete(f'/api/v1/settings/categories/{category_id}')
        
        if response.get('success'):
            return jsonify({
                'success': True,
                'message': response.get('message', 'Category deleted successfully')
            })
        else:
            return jsonify({
                'success': False,
                'message': response.get('message', 'Failed to delete category')
            })
            
    except Exception as e:
        print(f"Error deleting category: {e}")
        return jsonify({'success': False, 'message': 'Error deleting category'})

@system_settings_bp.route('/system-settings/api/categories')
@super_admin_required
def get_categories():
    """Get all categories using API"""
    try:
        response = api_client.get('/api/v1/settings/categories')
        
        if response.get('success'):
            return jsonify({
                'success': True,
                'categories': response.get('data', [])
            })
        else:
            return jsonify({
                'success': False,
                'message': response.get('message', 'Failed to load categories'),
                'categories': []
            })
            
    except Exception as e:
        print(f"Error getting categories: {e}")
        return jsonify({'success': False, 'message': 'Error loading categories', 'categories': []})

# --------------------------------------------------------------------------
# FAQ Management Routes - Now using API
# --------------------------------------------------------------------------

@system_settings_bp.route('/system-settings/save-faq', methods=['POST'])
@super_admin_required
def save_faq():
    """Create or update FAQ using API"""
    try:
        faq_id = request.form.get('faq_id')
        faq_data = {
            'question': request.form.get('question'),
            'answer': request.form.get('answer'),
            'category_id': int(request.form.get('category_id')),
            'is_active': 'is_active' in request.form,
            'order_index': int(request.form.get('order_index', 0))
        }
        
        if faq_id:
            # Update existing FAQ
            response = api_client.put(f'/api/v1/settings/faqs/{faq_id}', faq_data)
        else:
            # Create new FAQ
            response = api_client.post('/api/v1/settings/faqs', faq_data)
        
        if response.get('success'):
            return jsonify({
                'success': True,
                'message': response.get('message', 'FAQ saved successfully'),
                'faq': response.get('data', {})
            })
        else:
            return jsonify({
                'success': False,
                'message': response.get('message', 'Failed to save FAQ')
            })
            
    except Exception as e:
        print(f"Error saving FAQ: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error saving FAQ: {str(e)}'})

@system_settings_bp.route('/system-settings/delete-faq/<int:faq_id>', methods=['DELETE'])
@super_admin_required
def delete_faq(faq_id):
    """Delete FAQ using API"""
    try:
        response = api_client.delete(f'/api/v1/settings/faqs/{faq_id}')
        
        if response.get('success'):
            return jsonify({
                'success': True,
                'message': response.get('message', 'FAQ deleted successfully')
            })
        else:
            return jsonify({
                'success': False,
                'message': response.get('message', 'Failed to delete FAQ')
            })
            
    except Exception as e:
        print(f"Error deleting FAQ: {e}")
        return jsonify({'success': False, 'message': 'Error deleting FAQ'})

@system_settings_bp.route('/system-settings/api/faqs/<int:category_id>')
@super_admin_required
def get_faqs_by_category(category_id):
    """Get FAQs by category ID using API"""
    try:
        response = api_client.get('/api/v1/settings/faqs', {'category_id': category_id})
        
        if response.get('success'):
            return jsonify({
                'success': True,
                'faqs': response.get('data', [])
            })
        else:
            return jsonify({
                'success': False,
                'message': response.get('message', 'Failed to load FAQs'),
                'faqs': []
            })
            
    except Exception as e:
        print(f"Error getting FAQs: {e}")
        return jsonify({'success': False, 'message': 'Error loading FAQs', 'faqs': []})