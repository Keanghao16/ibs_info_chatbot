from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from ...database.connection import SessionLocal
from ...database.models import SystemSettings, FAQ
from ...services import SystemSettingService, FAQService
from sqlalchemy.orm import joinedload
from .auth import super_admin_required

system_settings_bp = Blueprint('system_settings', __name__)
system_setting_service = SystemSettingService()
faq_service = FAQService()

@system_settings_bp.route('/system-settings')
@super_admin_required
def index():
    """System settings page"""
    db = SessionLocal()
    try:
        settings = system_setting_service.get_settings(db)
        
        # Get all FAQs with their categories
        faqs = db.query(FAQ).options(joinedload(FAQ.faq_category)).order_by(
            FAQ.order_index, 
            FAQ.created_at
        ).all()
        
        # Get categories
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
        
        return render_template('system_setting/index.html', 
                             settings=settings, 
                             faqs=faqs_dict,
                             categories=categories_dict)
    finally:
        db.close()

@system_settings_bp.route('/system-settings/save-general', methods=['POST'])
@super_admin_required
def save_general_settings():
    """Save general system settings"""
    db = SessionLocal()
    try:
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
    """Save bot configuration settings"""
    db = SessionLocal()
    try:
        settings_data = {
            'response_timeout': request.form.get('response_timeout', 30),
            'offline_message': request.form.get('offline_message'),
            'enable_file_uploads': 'enable_file_uploads' in request.form,
            'enable_typing_indicator': 'enable_typing_indicator' in request.form
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
    """Save notification settings"""
    db = SessionLocal()
    try:
        settings_data = {
            'email_notifications': 'email_notifications' in request.form,
            'notify_new_user': 'notify_new_user' in request.form,
            'notify_new_chat': 'notify_new_chat' in request.form,
            'notify_unassigned_chat': 'notify_unassigned_chat' in request.form,
            'notification_email': request.form.get('notification_email')
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
#
# Category Management Routes
#
# --------------------------------------------------------------------------

@system_settings_bp.route('/system-settings/save-category', methods=['POST'])
@super_admin_required
def save_category():
    """Create or update FAQ category"""
    db = SessionLocal()
    try:
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

@system_settings_bp.route('/system-settings/delete-category/<int:category_id>', methods=['DELETE'])
@super_admin_required
def delete_category(category_id):
    """Delete FAQ category"""
    db = SessionLocal()
    try:
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

@system_settings_bp.route('/system-settings/api/categories')
@super_admin_required
def get_categories():
    """API endpoint to get all categories"""
    db = SessionLocal()
    try:
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
                'faq_count': faq_service.get_category_faq_count(db, cat.id)
            } for cat in categories]
        })
    finally:
        db.close()

# --------------------------------------------------------------------------
#
# FAQ Management Routes
#
# --------------------------------------------------------------------------

@system_settings_bp.route('/system-settings/save-faq', methods=['POST'])
@super_admin_required
def save_faq():
    """Save or update FAQ"""
    db = SessionLocal()
    try:
        faq_id = request.form.get('faq_id')
        question = request.form.get('question')
        answer = request.form.get('answer')
        category_id = int(request.form.get('category_id'))
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

@system_settings_bp.route('/system-settings/delete-faq/<int:faq_id>', methods=['DELETE'])
@super_admin_required
def delete_faq(faq_id):
    """Delete FAQ"""
    db = SessionLocal()
    try:
        success = faq_service.delete_faq(db, faq_id)
        
        if not success:
            return jsonify({'success': False, 'message': 'FAQ not found'})
        
        return jsonify({'success': True, 'message': 'FAQ deleted successfully'})
        
    except Exception as e:
        print(f"Error deleting FAQ: {e}")
        return jsonify({'success': False, 'message': 'Error deleting FAQ'})
    finally:
        db.close()

@system_settings_bp.route('/system-settings/api/faqs/<int:category_id>')
@super_admin_required
def get_faqs_by_category(category_id):
    """API endpoint to get FAQs by category ID"""
    db = SessionLocal()
    try:
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