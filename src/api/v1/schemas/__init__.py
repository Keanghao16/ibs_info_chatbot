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

__all__ = [
    # Schemas
    'BaseResponseSchema',
    'PaginationSchema',
    'ErrorDetailSchema',
    
    # Builder
    'ResponseBuilder',
    
    # Convenience functions
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
]