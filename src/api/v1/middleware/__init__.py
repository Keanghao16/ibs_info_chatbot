"""
API Middleware Package
Contains authentication and other middleware functions
"""

from .auth import (
    token_required,
    admin_required,
    super_admin_required,
    optional_auth  # Now it exists
)
from .cors import (
    configure_cors,
    add_cors_headers,
    cors_config,
    CORSConfig
)
from .error_handler import (
    register_error_handlers,
    APIError,
    abort_with_error,
    validate_request_json
)

__all__ = [
    # Authentication
    'token_required',
    'admin_required',
    'super_admin_required',
    'optional_auth',
    
    # CORS
    'configure_cors',
    'add_cors_headers',
    'cors_config',
    'CORSConfig',
    
    # Error Handling
    'register_error_handlers',
    'APIError',
    'abort_with_error',
    'validate_request_json'
]