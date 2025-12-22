"""
System Settings Data Schemas
Handles serialization and validation for FAQ and Category resources
"""

from marshmallow import Schema, fields, validate, validates, ValidationError


class CategoryResponseSchema(Schema):
    """Serialize FAQ category data"""
    
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    slug = fields.String(dump_only=True)
    description = fields.String(allow_none=True)
    icon = fields.String(allow_none=True)
    order_index = fields.Integer()
    is_active = fields.Boolean()
    faq_count = fields.Integer(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    
    class Meta:
        ordered = True


class CategoryListResponseSchema(Schema):
    """Serialize category list with minimal data"""
    
    id = fields.Integer()
    name = fields.String()
    slug = fields.String()
    icon = fields.String(allow_none=True)
    order_index = fields.Integer()
    is_active = fields.Boolean()
    faq_count = fields.Integer()


class CategoryCreateSchema(Schema):
    """Validate category creation request"""
    
    name = fields.String(
        required=True,
        validate=validate.Length(min=2, max=100)
    )
    description = fields.String(
        allow_none=True,
        validate=validate.Length(max=500)
    )
    icon = fields.String(
        allow_none=True,
        validate=validate.Length(max=50)
    )
    order_index = fields.Integer(
        load_default=0,
        validate=validate.Range(min=0)
    )
    is_active = fields.Boolean(load_default=True)


class CategoryUpdateSchema(Schema):
    """Validate category update request"""
    
    name = fields.String(
        validate=validate.Length(min=2, max=100)
    )
    description = fields.String(
        allow_none=True,
        validate=validate.Length(max=500)
    )
    icon = fields.String(
        allow_none=True,
        validate=validate.Length(max=50)
    )
    order_index = fields.Integer(
        validate=validate.Range(min=0)
    )
    is_active = fields.Boolean()


class FAQResponseSchema(Schema):
    """Serialize FAQ data"""
    
    id = fields.Integer(dump_only=True)
    category_id = fields.Integer()
    question = fields.String(required=True)
    answer = fields.String(required=True)
    order_index = fields.Integer()
    is_active = fields.Boolean()
    view_count = fields.Integer(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Nested category
    category = fields.Nested(CategoryListResponseSchema, dump_only=True)
    
    class Meta:
        ordered = True


class FAQListResponseSchema(Schema):
    """Serialize FAQ list with minimal data"""
    
    id = fields.Integer()
    category_id = fields.Integer()
    question = fields.String()
    answer = fields.String()
    order_index = fields.Integer()
    is_active = fields.Boolean()
    view_count = fields.Integer()
    category_name = fields.String()


class FAQCreateSchema(Schema):
    """Validate FAQ creation request"""
    
    category_id = fields.Integer(
        required=True,
        validate=validate.Range(min=1)
    )
    question = fields.String(
        required=True,
        validate=validate.Length(min=5, max=500)
    )
    answer = fields.String(
        required=True,
        validate=validate.Length(min=10, max=5000)
    )
    order_index = fields.Integer(
        load_default=0,
        validate=validate.Range(min=0)
    )
    is_active = fields.Boolean(load_default=True)
    
    @validates('question')
    def validate_question(self, value):
        """Ensure question ends with question mark"""
        if not value.strip().endswith('?'):
            raise ValidationError('Question should end with a question mark')


class FAQUpdateSchema(Schema):
    """Validate FAQ update request"""
    
    category_id = fields.Integer(
        validate=validate.Range(min=1)
    )
    question = fields.String(
        validate=validate.Length(min=5, max=500)
    )
    answer = fields.String(
        validate=validate.Length(min=10, max=5000)
    )
    order_index = fields.Integer(
        validate=validate.Range(min=0)
    )
    is_active = fields.Boolean()