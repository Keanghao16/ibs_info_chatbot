"""
User Data Schemas
Handles serialization and validation for User resources
"""

from marshmallow import Schema, fields, validate, validates, ValidationError, pre_load
import html


class UserResponseSchema(Schema):
    """Serialize user data for API responses"""
    
    id = fields.String(dump_only=True)  # ✅ Changed to String (UUID)
    telegram_id = fields.Integer(required=True)
    username = fields.String(allow_none=True)
    first_name = fields.String(allow_none=True)
    last_name = fields.String(allow_none=True)
    full_name = fields.String(dump_only=True)
    language_code = fields.String(allow_none=True)
    is_bot = fields.Boolean()
    is_premium = fields.Boolean()
    registration_date = fields.DateTime(dump_only=True)
    last_activity = fields.DateTime(allow_none=True)
    total_chats = fields.Integer(dump_only=True)
    
    class Meta:
        ordered = True


class UserListResponseSchema(Schema):
    """Serialize user list with minimal data"""
    
    id = fields.String()  # ✅ Changed to String
    telegram_id = fields.Integer()
    username = fields.String(allow_none=True)
    full_name = fields.String()
    is_premium = fields.Boolean()
    registration_date = fields.DateTime()
    total_chats = fields.Integer()
    last_activity = fields.DateTime(allow_none=True)


class UserCreateSchema(Schema):
    """Validate user creation request"""
    
    telegram_id = fields.Integer(
        required=True,
        validate=validate.Range(min=1, error="Invalid Telegram ID")
    )
    username = fields.String(
        allow_none=True,
        validate=validate.Length(max=100)
    )
    first_name = fields.String(
        allow_none=True,
        validate=validate.Length(max=100)
    )
    last_name = fields.String(
        allow_none=True,
        validate=validate.Length(max=100)
    )
    language_code = fields.String(
        allow_none=True,
        validate=validate.Length(max=10)
    )
    is_bot = fields.Boolean(load_default=False)
    is_premium = fields.Boolean(load_default=False)
    
    @pre_load
    def sanitize_input(self, data, **kwargs):
        """Sanitize string inputs to prevent XSS"""
        if data.get('username'):
            data['username'] = html.escape(data['username'].strip())
        if data.get('first_name'):
            data['first_name'] = html.escape(data['first_name'].strip())
        if data.get('last_name'):
            data['last_name'] = html.escape(data['last_name'].strip())
        return data


class UserUpdateSchema(Schema):
    """Validate user update request"""
    
    username = fields.String(
        allow_none=True,
        validate=validate.Length(max=100)
    )
    first_name = fields.String(
        allow_none=True,
        validate=validate.Length(max=100)
    )
    last_name = fields.String(
        allow_none=True,
        validate=validate.Length(max=100)
    )
    language_code = fields.String(
        allow_none=True,
        validate=validate.Length(max=10)
    )
    is_premium = fields.Boolean()


class UserStatsSchema(Schema):
    """User statistics response"""
    
    total_users = fields.Integer()
    active_today = fields.Integer()
    active_this_week = fields.Integer()
    active_this_month = fields.Integer()
    premium_users = fields.Integer()
    bot_users = fields.Integer()
    new_users_today = fields.Integer()
    new_users_this_week = fields.Integer()
    new_users_this_month = fields.Integer()