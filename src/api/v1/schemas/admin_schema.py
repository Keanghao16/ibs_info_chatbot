"""
Admin Data Schemas
"""

from marshmallow import Schema, fields, validate, validates, ValidationError


class AdminResponseSchema(Schema):
    """Serialize admin data for API responses"""
    
    id = fields.String(dump_only=True)  #  UUID
    telegram_id = fields.String(required=True)
    telegram_username = fields.String(allow_none=True)
    full_name = fields.String(allow_none=True)
    role = fields.String()
    is_active = fields.Boolean()
    is_available = fields.Boolean()
    division = fields.String(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    last_login = fields.DateTime(allow_none=True)
    
    class Meta:
        ordered = True


class AdminListResponseSchema(Schema):
    """Serialize admin list with minimal data"""
    
    id = fields.String()  #  UUID
    telegram_id = fields.String()
    telegram_username = fields.String(allow_none=True)
    full_name = fields.String()
    role = fields.String()
    is_active = fields.Boolean()
    is_available = fields.Boolean()
    last_login = fields.DateTime(allow_none=True)


class AdminCreateSchema(Schema):
    """Validate admin creation request"""
    
    telegram_id = fields.String(
        required=True,
        validate=validate.Length(min=1, max=50)
    )
    username = fields.String(
        allow_none=True,
        validate=validate.Length(max=100)
    )
    full_name = fields.String(
        required=True,
        validate=validate.Length(min=2, max=255)
    )
    role = fields.String(
        load_default='admin',
        validate=validate.OneOf(['admin', 'super_admin'])
    )
    division = fields.String(
        allow_none=True,
        validate=validate.Length(max=100)
    )


class AdminUpdateSchema(Schema):
    """Validate admin update request"""
    
    full_name = fields.String(
        validate=validate.Length(min=2, max=255)
    )
    role = fields.String(
        validate=validate.OneOf(['admin', 'super_admin'])
    )
    division = fields.String(
        allow_none=True,
        validate=validate.Length(max=100)
    )


class AdminStatsSchema(Schema):
    """Admin statistics response"""
    
    total_admins = fields.Integer()
    active_admins = fields.Integer()
    available_admins = fields.Integer()
    super_admins = fields.Integer()
    regular_admins = fields.Integer()  # ✅ Added
    online_now = fields.Integer()