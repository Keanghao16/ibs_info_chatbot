"""
Error Handler Middleware
Provides consistent error responses across all API endpoints
"""

from flask import jsonify, request
from werkzeug.exceptions import HTTPException
import traceback
import logging

# Setup logger
logger = logging.getLogger(__name__)


class APIError(Exception):
    """
    Custom API Error class for raising exceptions with specific status codes
    
    Usage:
        raise APIError("Resource not found", status_code=404)
    """
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload
    
    def to_dict(self):
        """Convert error to dictionary format"""
        rv = dict(self.payload or ())
        rv['success'] = False
        rv['message'] = self.message
        rv['status_code'] = self.status_code
        return rv


def register_error_handlers(app):
    """
    Register all error handlers for the Flask application
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(APIError)
    def handle_api_error(error):
        """Handle custom API errors"""
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    
    @app.errorhandler(400)
    def bad_request(error):
        """
        Handle 400 Bad Request errors
        Raised when request data is invalid or malformed
        """
        logger.warning(f"400 Bad Request: {request.path} - {str(error)}")
        
        return jsonify({
            'success': False,
            'error': 'bad_request',
            'message': str(error.description) if hasattr(error, 'description') else 'Invalid request data',
            'status_code': 400,
            'path': request.path
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        """
        Handle 401 Unauthorized errors
        Raised when authentication is required but not provided or invalid
        """
        logger.warning(f"401 Unauthorized: {request.path}")
        
        return jsonify({
            'success': False,
            'error': 'unauthorized',
            'message': str(error.description) if hasattr(error, 'description') else 'Authentication required',
            'status_code': 401,
            'path': request.path
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        """
        Handle 403 Forbidden errors
        Raised when user doesn't have permission to access resource
        """
        logger.warning(f"403 Forbidden: {request.path}")
        
        return jsonify({
            'success': False,
            'error': 'forbidden',
            'message': str(error.description) if hasattr(error, 'description') else 'Access denied',
            'status_code': 403,
            'path': request.path
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        """
        Handle 404 Not Found errors
        Raised when requested resource doesn't exist
        """
        logger.info(f"404 Not Found: {request.path}")
        
        return jsonify({
            'success': False,
            'error': 'not_found',
            'message': str(error.description) if hasattr(error, 'description') else 'Resource not found',
            'status_code': 404,
            'path': request.path
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """
        Handle 405 Method Not Allowed errors
        Raised when HTTP method is not allowed for the endpoint
        """
        logger.warning(f"405 Method Not Allowed: {request.method} {request.path}")
        
        return jsonify({
            'success': False,
            'error': 'method_not_allowed',
            'message': str(error.description) if hasattr(error, 'description') else 'HTTP method not allowed',
            'status_code': 405,
            'path': request.path,
            'allowed_methods': error.valid_methods if hasattr(error, 'valid_methods') else None
        }), 405
    
    @app.errorhandler(422)
    def unprocessable_entity(error):
        """
        Handle 422 Unprocessable Entity errors
        Raised when request is well-formed but contains validation errors
        """
        logger.warning(f"422 Unprocessable Entity: {request.path}")
        
        return jsonify({
            'success': False,
            'error': 'validation_error',
            'message': str(error.description) if hasattr(error, 'description') else 'Validation failed',
            'status_code': 422,
            'path': request.path
        }), 422
    
    @app.errorhandler(429)
    def too_many_requests(error):
        """
        Handle 429 Too Many Requests errors
        Raised when rate limit is exceeded
        """
        logger.warning(f"429 Too Many Requests: {request.path}")
        
        return jsonify({
            'success': False,
            'error': 'rate_limit_exceeded',
            'message': 'Too many requests. Please try again later.',
            'status_code': 429,
            'path': request.path
        }), 429
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """
        Handle 500 Internal Server Error
        Raised when an unexpected error occurs
        """
        logger.error(f"500 Internal Server Error: {request.path}")
        logger.error(traceback.format_exc())
        
        # In production, don't expose error details
        is_debug = app.config.get('DEBUG', False)
        
        response = {
            'success': False,
            'error': 'internal_server_error',
            'message': 'An unexpected error occurred',
            'status_code': 500,
            'path': request.path
        }
        
        # Add error details in debug mode
        if is_debug:
            response['error_details'] = str(error)
            response['traceback'] = traceback.format_exc()
        
        return jsonify(response), 500
    
    @app.errorhandler(503)
    def service_unavailable(error):
        """
        Handle 503 Service Unavailable errors
        Raised when service is temporarily unavailable
        """
        logger.error(f"503 Service Unavailable: {request.path}")
        
        return jsonify({
            'success': False,
            'error': 'service_unavailable',
            'message': 'Service temporarily unavailable. Please try again later.',
            'status_code': 503,
            'path': request.path
        }), 503
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """
        Handle all other HTTP exceptions
        Fallback handler for any HTTP exception not explicitly handled
        """
        logger.warning(f"{error.code} HTTP Exception: {request.path} - {str(error)}")
        
        return jsonify({
            'success': False,
            'error': error.name.lower().replace(' ', '_'),
            'message': error.description or 'An HTTP error occurred',
            'status_code': error.code,
            'path': request.path
        }), error.code
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """
        Handle all uncaught exceptions
        Last resort error handler for any unhandled exception
        """
        logger.critical(f"Unhandled exception: {request.path}")
        logger.critical(traceback.format_exc())
        
        # In production, don't expose error details
        is_debug = app.config.get('DEBUG', False)
        
        response = {
            'success': False,
            'error': 'internal_error',
            'message': 'An unexpected error occurred',
            'status_code': 500,
            'path': request.path
        }
        
        # Add error details in debug mode
        if is_debug:
            response['error_type'] = type(error).__name__
            response['error_details'] = str(error)
            response['traceback'] = traceback.format_exc()
        
        return jsonify(response), 500
    
    # Log successful registration
    logger.info(" Error handlers registered")
    print(" Error handlers registered")


def abort_with_error(message, status_code=400, **kwargs):
    """
    Helper function to abort request with error
    
    Args:
        message: Error message
        status_code: HTTP status code
        **kwargs: Additional data to include in error response
        
    Usage:
        from .middleware.error_handler import abort_with_error
        abort_with_error("User not found", status_code=404, user_id=123)
    """
    raise APIError(message, status_code=status_code, payload=kwargs)


def validate_request_json(required_fields=None):
    """
    Decorator to validate JSON request body
    
    Args:
        required_fields: List of required field names
        
    Usage:
        @validate_request_json(['name', 'email'])
        def create_user():
            data = request.get_json()
            # data is guaranteed to have 'name' and 'email'
    """
    def decorator(f):
        from functools import wraps
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if request has JSON
            if not request.is_json:
                raise APIError(
                    "Request must be JSON",
                    status_code=400,
                    payload={'content_type': request.content_type}
                )
            
            data = request.get_json()
            
            # Check if data is provided
            if not data:
                raise APIError(
                    "Request body cannot be empty",
                    status_code=400
                )
            
            # Validate required fields
            if required_fields:
                missing_fields = []
                for field in required_fields:
                    if field not in data or data[field] is None or str(data[field]).strip() == '':
                        missing_fields.append(field)
                
                if missing_fields:
                    raise APIError(
                        f"Missing required fields: {', '.join(missing_fields)}",
                        status_code=422,
                        payload={'missing_fields': missing_fields}
                    )
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator