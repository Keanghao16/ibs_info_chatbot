"""
API Schemas Package
Contains all request/response validation schemas
"""

from .response_schema import (
    BaseResponseSchema,
    PaginationSchema,
    ErrorDetailSchema,
    ResponseBuilder,
    success_response,
    error_response,
    paginated_response,
    validation_error_response,
    not_found_response,
    unauthorized_response,
    forbidden_response,
    created_response,
    updated_response,
    deleted_response
)

from .user_schema import (
    UserResponseSchema,
    UserListResponseSchema,
    UserCreateSchema,
    UserUpdateSchema,
    UserStatsSchema
)

from .admin_schema import (
    AdminResponseSchema,
    AdminListResponseSchema,
    AdminCreateSchema,
    AdminUpdateSchema,
    # AdminPasswordUpdateSchema,  # ❌ Remove if not needed
    # AdminLoginSchema,  # ❌ Remove if not needed
    AdminStatsSchema
)

from .chat_schema import (
    ChatMessageResponseSchema,
    ChatSessionResponseSchema,
    ChatSessionListResponseSchema,
    ChatSessionCreateSchema,
    ChatSessionUpdateSchema,
    MessageCreateSchema,
    ChatAssignSchema,
    ChatStatsSchema
)

from .system_setting_schema import (
    CategoryResponseSchema,
    CategoryListResponseSchema,
    CategoryCreateSchema,
    CategoryUpdateSchema,
    FAQResponseSchema,
    FAQListResponseSchema,
    FAQCreateSchema,
    FAQUpdateSchema
)

__all__ = [
    # Response schemas
    'BaseResponseSchema',
    'PaginationSchema',
    'ErrorDetailSchema',
    'ResponseBuilder',
    'success_response',
    'error_response',
    'paginated_response',
    'validation_error_response',
    'not_found_response',
    'unauthorized_response',
    'forbidden_response',
    'created_response',
    'updated_response',
    'deleted_response',
    
    # User schemas
    'UserResponseSchema',
    'UserListResponseSchema',
    'UserCreateSchema',
    'UserUpdateSchema',
    'UserStatsSchema',
    
    # Admin schemas
    'AdminResponseSchema',
    'AdminListResponseSchema',
    'AdminCreateSchema',
    'AdminUpdateSchema',
    # 'AdminPasswordUpdateSchema',  # ❌ Remove
    # 'AdminLoginSchema',  # ❌ Remove
    'AdminStatsSchema',
    
    # Chat schemas
    'ChatMessageResponseSchema',
    'ChatSessionResponseSchema',
    'ChatSessionListResponseSchema',
    'ChatSessionCreateSchema',
    'ChatSessionUpdateSchema',
    'MessageCreateSchema',
    'ChatAssignSchema',
    'ChatStatsSchema',
    
    # System settings schemas
    'CategoryResponseSchema',
    'CategoryListResponseSchema',
    'CategoryCreateSchema',
    'CategoryUpdateSchema',
    'FAQResponseSchema',
    'FAQListResponseSchema',
    'FAQCreateSchema',
    'FAQUpdateSchema',
]