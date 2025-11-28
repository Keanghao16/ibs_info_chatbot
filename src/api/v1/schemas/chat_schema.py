"""
Chat Data Schemas
Handles serialization and validation for Chat resources
"""

from marshmallow import Schema, fields, validate, validates, ValidationError
from datetime import datetime


class ChatMessageResponseSchema(Schema):
    """Serialize chat message data"""
    
    id = fields.Integer(dump_only=True)
    session_id = fields.Integer()
    user_id = fields.String()  # ✅ Changed to String (UUID)
    admin_id = fields.String(allow_none=True)  # ✅ Changed to String (UUID)
    message = fields.String()
    timestamp = fields.DateTime(dump_only=True)
    is_from_admin = fields.Boolean()
    
    class Meta:
        ordered = True


class ChatSessionResponseSchema(Schema):
    """Serialize chat session data for API responses"""
    
    id = fields.Integer(dump_only=True)
    user_id = fields.String()  # ✅ Changed to String (UUID)
    admin_id = fields.String(allow_none=True)  # ✅ Changed to String (UUID)
    status = fields.String()
    start_time = fields.DateTime(dump_only=True)
    end_time = fields.DateTime(allow_none=True)
    duration_seconds = fields.Integer(dump_only=True)
    message_count = fields.Integer(dump_only=True)
    
    # Nested relationships
    user = fields.Nested('UserListResponseSchema', dump_only=True)
    admin = fields.Nested('AdminListResponseSchema', dump_only=True, allow_none=True)
    messages = fields.List(fields.Nested(ChatMessageResponseSchema), dump_only=True)
    
    class Meta:
        ordered = True


class ChatSessionListResponseSchema(Schema):
    """Serialize chat session list with minimal data"""
    
    id = fields.Integer()
    user_id = fields.String()  # ✅ Changed to String (UUID)
    admin_id = fields.String(allow_none=True)  # ✅ Changed to String (UUID)
    status = fields.String()
    start_time = fields.DateTime()
    end_time = fields.DateTime(allow_none=True)
    message_count = fields.Integer()
    user_name = fields.String()
    admin_name = fields.String(allow_none=True)


class ChatSessionCreateSchema(Schema):
    """Validate chat session creation request"""
    
    user_id = fields.String(  # ✅ Changed to String (UUID)
        required=True,
        validate=validate.Length(min=1, max=36)  # UUID length
    )
    status = fields.String(
        load_default='waiting',
        validate=validate.OneOf(['waiting', 'active', 'closed'])
    )


class ChatSessionUpdateSchema(Schema):
    """Validate chat session update request"""
    
    status = fields.String(
        validate=validate.OneOf(['waiting', 'active', 'closed'])
    )
    admin_id = fields.String(  # ✅ Changed to String (UUID)
        allow_none=True,
        validate=validate.Length(min=1, max=36)
    )


class MessageCreateSchema(Schema):
    """Validate message creation request"""
    
    session_id = fields.Integer(
        required=True,
        validate=validate.Range(min=1)
    )
    user_id = fields.String(  # ✅ Changed to String (UUID)
        required=True,
        validate=validate.Length(min=1, max=36)
    )
    admin_id = fields.String(  # ✅ Changed to String (UUID)
        allow_none=True,
        validate=validate.Length(min=1, max=36)
    )
    message = fields.String(
        required=True,
        validate=validate.Length(min=1, max=4096)
    )
    is_from_admin = fields.Boolean(
        load_default=False
    )
    
    @validates('message')
    def validate_message_not_empty(self, value):
        """Ensure message is not empty or whitespace only"""
        if not value.strip():
            raise ValidationError('Message cannot be empty')


class ChatAssignSchema(Schema):
    """Validate chat assignment request"""
    
    admin_id = fields.String(  # ✅ Changed to String (UUID)
        required=True,
        validate=validate.Length(min=1, max=36)
    )


class ChatStatsSchema(Schema):
    """Chat statistics response"""
    
    total_sessions = fields.Integer()
    active_sessions = fields.Integer()
    waiting_sessions = fields.Integer()
    closed_sessions = fields.Integer()
    total_messages = fields.Integer()
    average_response_time = fields.Float()
    average_session_duration = fields.Float()