"""
System Settings API Routes
Handles FAQ categories and FAQ management endpoints
"""

from flask import Blueprint, request, jsonify
from ..middleware.auth import token_required, admin_required
from ..schemas import (
    CategoryResponseSchema,
    CategoryListResponseSchema,
    CategoryCreateSchema,
    CategoryUpdateSchema,
    FAQResponseSchema,
    FAQListResponseSchema,
    FAQCreateSchema,
    FAQUpdateSchema,
    success_response,
    error_response,
    paginated_response,
    created_response,
    updated_response,
    deleted_response,
    not_found_response,
    validation_error_response
)
from ....services.system_setting_service import SystemSettingService
from ....database.connection import get_db_session
from ....database.models import FAQCategory, FAQ
from marshmallow import ValidationError
import re  # ✅ ADD THIS LINE
import traceback  # ✅ ADD THIS LINE

# Create blueprint
settings_api_bp = Blueprint('settings_api', __name__)

# Initialize schemas
category_response_schema = CategoryResponseSchema()
category_list_schema = CategoryListResponseSchema(many=True)
category_create_schema = CategoryCreateSchema()
category_update_schema = CategoryUpdateSchema()
faq_response_schema = FAQResponseSchema()
faq_list_schema = FAQListResponseSchema(many=True)
faq_create_schema = FAQCreateSchema()
faq_update_schema = FAQUpdateSchema()


# ============================================
# FAQ Categories Endpoints
# ============================================

@settings_api_bp.route('/settings/categories', methods=['GET'])
def list_categories():
    """Get all FAQ categories (public endpoint)"""
    db = get_db_session()
    try:
        categories = SystemSettingService.get_all_categories(db)
        
        # Add FAQ count to each category
        categories_with_count = []
        for category in categories:
            category_dict = {
                'id': category.id,
                'name': category.name,
                'slug': category.slug,
                'description': category.description,
                'icon': category.icon,
                'is_active': category.is_active,
                'order_index': category.order_index,
                'faq_count': len(category.faqs) if hasattr(category, 'faqs') else 0
            }
            categories_with_count.append(category_dict)
        
        return success_response(
            data=categories_with_count,
            message=f"Retrieved {len(categories_with_count)} categories"
        )
        
    except Exception as e:
        return error_response(str(e), 500)
    finally:
        db.close()


@settings_api_bp.route('/settings/categories/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """Get single category (public endpoint)"""
    db = get_db_session()
    try:
        category = SystemSettingService.get_category_by_id(db, category_id)
        
        if not category:
            return not_found_response('Category')
        
        category_data = category_response_schema.dump(category)
        
        return success_response(
            data=category_data,
            message="Category retrieved successfully"
        )
        
    except Exception as e:
        return error_response(str(e), 500)
    finally:
        db.close()


@settings_api_bp.route('/settings/categories', methods=['POST'])
@token_required
@admin_required
def create_category(current_user):
    """
    Create new FAQ category
    
    Request Body:
        {
            "name": "Getting Started",
            "description": "Basic information",
            "icon": "📚",
            "order_index": 0,
            "is_active": true
        }
    
    Note: slug will be auto-generated from name
    """
    db = get_db_session()
    try:
        # Validate request data
        try:
            category_data = category_create_schema.load(request.json)
        except ValidationError as err:
            return validation_error_response(err.messages)
        
        # ✅ Auto-generate slug from name
        name = category_data.get('name', '')
        # Convert to lowercase, replace spaces with hyphens, remove special chars
        slug = re.sub(r'[^a-z0-9-]', '', name.lower().replace(' ', '-'))
        
        # ✅ Ensure slug is not empty
        if not slug:
            return error_response(
                "Category name must contain at least one alphanumeric character",
                400
            )
        
        category_data['slug'] = slug
        
        # ✅ Check if slug already exists
        existing = db.query(FAQCategory).filter(FAQCategory.slug == slug).first()
        if existing:
            return error_response(
                f"Category with name '{name}' already exists (slug: '{slug}'). Please use a different name.",
                400
            )
        
        # ✅ Handle emoji encoding issue
        icon = category_data.get('icon', '')
        if icon:
            try:
                # Ensure icon can be encoded properly
                icon.encode('utf-8')
            except UnicodeEncodeError:
                category_data['icon'] = '📁'  # Default icon if encoding fails
        
        # Create category using service
        new_category = SystemSettingService.create_category(db, category_data)
        
        category_response = {
            'id': new_category.id,
            'name': new_category.name,
            'slug': new_category.slug,
            'description': new_category.description,
            'icon': new_category.icon,
            'is_active': new_category.is_active,
            'order_index': new_category.order_index,
            'created_at': new_category.created_at.isoformat() if new_category.created_at else None
        }
        
        return created_response(
            data=category_response,
            message="Category created successfully"
        )
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating category: {str(e)}")
        traceback.print_exc()
        
        # Check if it's a MySQL charset issue
        if 'Incorrect string value' in str(e):
            return error_response(
                "Unable to save emoji. Please use text-only icons or update database charset to utf8mb4.",
                400
            )
        
        return error_response(str(e), 500)
    finally:
        db.close()


@settings_api_bp.route('/settings/categories/<int:category_id>', methods=['PUT'])
@token_required
@admin_required
def update_category(current_user, category_id):
    """Update FAQ category"""
    db = get_db_session()
    try:
        category = SystemSettingService.get_category_by_id(db, category_id)
        if not category:
            return not_found_response('Category')
        
        try:
            update_data = category_update_schema.load(request.json)
        except ValidationError as err:
            return validation_error_response(err.messages)
        
        # If name is being updated, regenerate slug
        if 'name' in update_data:
            new_slug = re.sub(r'[^a-z0-9-]', '', update_data['name'].lower().replace(' ', '-'))
            
            # Check if new slug conflicts with other categories
            existing = db.query(FAQCategory).filter(
                FAQCategory.slug == new_slug,
                FAQCategory.id != category_id
            ).first()
            
            if existing:
                return error_response(
                    f"Another category already uses the slug '{new_slug}'. Please use a different name.",
                    400
                )
            
            update_data['slug'] = new_slug
        
        updated_category = SystemSettingService.update_category(
            db, category_id, update_data
        )
        
        category_response = category_response_schema.dump(updated_category)
        
        return updated_response(
            data=category_response,
            message="Category updated successfully"
        )
        
    except Exception as e:
        db.rollback()
        return error_response(str(e), 500)
    finally:
        db.close()


@settings_api_bp.route('/settings/categories/<int:category_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_category(current_user, category_id):
    """Delete FAQ category"""
    db = get_db_session()
    try:
        category = SystemSettingService.get_category_by_id(db, category_id)
        if not category:
            return not_found_response('Category')
        
        # Check if category has FAQs
        faq_count = db.query(FAQ).filter(FAQ.category_id == category_id).count()
        if faq_count > 0:
            return error_response(
                f"Cannot delete category. It contains {faq_count} FAQ(s). Please delete or move the FAQs first.",
                400
            )
        
        SystemSettingService.delete_category(db, category_id)
        
        return deleted_response(message="Category deleted successfully")
        
    except Exception as e:
        db.rollback()
        return error_response(str(e), 500)
    finally:
        db.close()


# ============================================
# FAQs Endpoints
# ============================================

@settings_api_bp.route('/settings/faqs', methods=['GET'])
def list_faqs():
    """
    Get all FAQs (public endpoint)
    
    Query Parameters:
        - category_id (int): Filter by category
        - search (str): Search in questions/answers
        - is_active (bool): Filter by active status
    """
    db = get_db_session()
    try:
        category_id = request.args.get('category_id', type=int)
        search = request.args.get('search', '').strip()
        is_active_str = request.args.get('is_active', '').lower()
        is_active = is_active_str == 'true' if is_active_str else None
        
        faqs = SystemSettingService.get_all_faqs(
            db=db,
            category_id=category_id,
            search=search,
            is_active=is_active
        )
        
        faqs_data = faq_list_schema.dump(faqs)
        
        return success_response(
            data=faqs_data,
            message=f"Retrieved {len(faqs_data)} FAQs"
        )
        
    except Exception as e:
        return error_response(str(e), 500)
    finally:
        db.close()


@settings_api_bp.route('/settings/faqs/<int:faq_id>', methods=['GET'])
def get_faq(faq_id):
    """Get single FAQ (public endpoint)"""
    db = get_db_session()
    try:
        faq = SystemSettingService.get_faq_by_id(db, faq_id)
        
        if not faq:
            return not_found_response('FAQ')
        
        # Increment view count
        SystemSettingService.increment_faq_view_count(db, faq_id)
        
        faq_data = faq_response_schema.dump(faq)
        
        return success_response(
            data=faq_data,
            message="FAQ retrieved successfully"
        )
        
    except Exception as e:
        return error_response(str(e), 500)
    finally:
        db.close()


@settings_api_bp.route('/settings/faqs', methods=['POST'])
@token_required
@admin_required
def create_faq(current_user):
    """
    Create new FAQ
    
    Request Body:
        {
            "category_id": 1,
            "question": "How do I start?",
            "answer": "Send /start command",
            "order_index": 0,
            "is_active": true
        }
    """
    db = get_db_session()
    try:
        try:
            faq_data = faq_create_schema.load(request.json)
        except ValidationError as err:
            return validation_error_response(err.messages)
        
        # Verify category exists
        category = db.query(FAQCategory).filter(
            FAQCategory.id == faq_data['category_id']
        ).first()
        
        if not category:
            return error_response(
                f"Category with ID {faq_data['category_id']} not found",
                404
            )
        
        new_faq = SystemSettingService.create_faq(db, faq_data)
        
        faq_response = faq_response_schema.dump(new_faq)
        
        return created_response(
            data=faq_response,
            message="FAQ created successfully"
        )
        
    except Exception as e:
        db.rollback()
        import traceback
        print(f"Error creating FAQ: {str(e)}")
        traceback.print_exc()
        return error_response(str(e), 500)
    finally:
        db.close()


@settings_api_bp.route('/settings/faqs/<int:faq_id>', methods=['PUT'])
@token_required
@admin_required
def update_faq(current_user, faq_id):
    """Update FAQ"""
    db = get_db_session()
    try:
        faq = SystemSettingService.get_faq_by_id(db, faq_id)
        if not faq:
            return not_found_response('FAQ')
        
        try:
            update_data = faq_update_schema.load(request.json)
        except ValidationError as err:
            return validation_error_response(err.messages)
        
        # Verify category exists if updating category_id
        if 'category_id' in update_data:
            category = db.query(FAQCategory).filter(
                FAQCategory.id == update_data['category_id']
            ).first()
            
            if not category:
                return error_response(
                    f"Category with ID {update_data['category_id']} not found",
                    404
                )
        
        updated_faq = SystemSettingService.update_faq(db, faq_id, update_data)
        
        faq_response = faq_response_schema.dump(updated_faq)
        
        return updated_response(
            data=faq_response,
            message="FAQ updated successfully"
        )
        
    except Exception as e:
        db.rollback()
        return error_response(str(e), 500)
    finally:
        db.close()


@settings_api_bp.route('/settings/faqs/<int:faq_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_faq(current_user, faq_id):
    """Delete FAQ"""
    db = get_db_session()
    try:
        faq = SystemSettingService.get_faq_by_id(db, faq_id)
        if not faq:
            return not_found_response('FAQ')
        
        SystemSettingService.delete_faq(db, faq_id)
        
        return deleted_response(message="FAQ deleted successfully")
        
    except Exception as e:
        db.rollback()
        return error_response(str(e), 500)
    finally:
        db.close()