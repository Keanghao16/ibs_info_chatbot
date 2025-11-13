"""
Standardized JSON Response Schema
Provides consistent response format across all API endpoints
"""

from typing import Any, Dict, List, Optional
from marshmallow import Schema, fields, post_dump


class PaginationSchema(Schema):
    """
    Pagination metadata schema
    """
    page = fields.Integer(required=True, description="Current page number")
    per_page = fields.Integer(required=True, description="Items per page")
    total = fields.Integer(required=True, description="Total number of items")
    total_pages = fields.Integer(required=True, description="Total number of pages")
    has_next = fields.Boolean(description="Whether there is a next page")
    has_prev = fields.Boolean(description="Whether there is a previous page")
    
    @post_dump
    def add_navigation_flags(self, data, **kwargs):
        """Add navigation flags based on pagination data"""
        data['has_next'] = data['page'] < data['total_pages']
        data['has_prev'] = data['page'] > 1
        return data


class ErrorDetailSchema(Schema):
    """
    Individual error detail schema
    """
    field = fields.String(description="Field that caused the error")
    message = fields.String(required=True, description="Error message")
    code = fields.String(description="Error code for programmatic handling")


class BaseResponseSchema(Schema):
    """
    Base response schema for all API responses
    """
    success = fields.Boolean(required=True, description="Request success status")
    message = fields.String(description="Human-readable message")
    data = fields.Raw(allow_none=True, description="Response data")
    errors = fields.List(fields.Nested(ErrorDetailSchema), description="List of errors if any")
    pagination = fields.Nested(PaginationSchema, allow_none=True, description="Pagination metadata")
    timestamp = fields.DateTime(description="Response timestamp")
    
    @post_dump
    def remove_none_values(self, data, **kwargs):
        """Remove None values from response"""
        return {key: value for key, value in data.items() if value is not None}


class ResponseBuilder:
    """
    Helper class to build standardized API responses
    """
    
    @staticmethod
    def success(
        data: Any = None,
        message: str = "Request successful",
        pagination: Optional[Dict] = None,
        status_code: int = 200
    ) -> tuple:
        """
        Build a success response
        
        Args:
            data: Response data (dict, list, or any serializable object)
            message: Success message
            pagination: Pagination metadata
            status_code: HTTP status code
            
        Returns:
            Tuple of (response_dict, status_code)
        """
        response = {
            'success': True,
            'message': message,
            'data': data
        }
        
        if pagination:
            response['pagination'] = pagination
        
        return response, status_code
    
    @staticmethod
    def error(
        message: str = "Request failed",
        errors: Optional[List[Dict]] = None,
        status_code: int = 400,
        data: Any = None
    ) -> tuple:
        """
        Build an error response
        
        Args:
            message: Error message
            errors: List of error details
            status_code: HTTP status code
            data: Optional additional data
            
        Returns:
            Tuple of (response_dict, status_code)
        """
        response = {
            'success': False,
            'message': message
        }
        
        if errors:
            response['errors'] = errors
        
        if data is not None:
            response['data'] = data
        
        return response, status_code
    
    @staticmethod
    def paginated_success(
        data: List,
        page: int,
        per_page: int,
        total: int,
        message: str = "Request successful",
        status_code: int = 200
    ) -> tuple:
        """
        Build a paginated success response
        
        Args:
            data: List of items for current page
            page: Current page number
            per_page: Items per page
            total: Total number of items
            message: Success message
            status_code: HTTP status code
            
        Returns:
            Tuple of (response_dict, status_code)
        """
        total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0
        
        pagination = {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
        
        return ResponseBuilder.success(
            data=data,
            message=message,
            pagination=pagination,
            status_code=status_code
        )
    
    @staticmethod
    def validation_error(
        errors: List[Dict],
        message: str = "Validation failed"
    ) -> tuple:
        """
        Build a validation error response
        
        Args:
            errors: List of validation errors
            message: Error message
            
        Returns:
            Tuple of (response_dict, status_code)
        """
        return ResponseBuilder.error(
            message=message,
            errors=errors,
            status_code=422
        )
    
    @staticmethod
    def not_found(
        message: str = "Resource not found",
        resource_type: str = None
    ) -> tuple:
        """
        Build a not found error response
        
        Args:
            message: Error message
            resource_type: Type of resource not found
            
        Returns:
            Tuple of (response_dict, status_code)
        """
        if resource_type:
            message = f"{resource_type} not found"
        
        return ResponseBuilder.error(
            message=message,
            status_code=404
        )
    
    @staticmethod
    def unauthorized(
        message: str = "Authentication required"
    ) -> tuple:
        """
        Build an unauthorized error response
        
        Args:
            message: Error message
            
        Returns:
            Tuple of (response_dict, status_code)
        """
        return ResponseBuilder.error(
            message=message,
            status_code=401
        )
    
    @staticmethod
    def forbidden(
        message: str = "Access denied"
    ) -> tuple:
        """
        Build a forbidden error response
        
        Args:
            message: Error message
            
        Returns:
            Tuple of (response_dict, status_code)
        """
        return ResponseBuilder.error(
            message=message,
            status_code=403
        )
    
    @staticmethod
    def bad_request(
        message: str = "Bad request",
        errors: Optional[List[Dict]] = None
    ) -> tuple:
        """
        Build a bad request error response
        
        Args:
            message: Error message
            errors: List of error details
            
        Returns:
            Tuple of (response_dict, status_code)
        """
        return ResponseBuilder.error(
            message=message,
            errors=errors,
            status_code=400
        )
    
    @staticmethod
    def internal_error(
        message: str = "Internal server error",
        include_details: bool = False,
        error_details: str = None
    ) -> tuple:
        """
        Build an internal server error response
        
        Args:
            message: Error message
            include_details: Whether to include error details (only in debug mode)
            error_details: Detailed error information
            
        Returns:
            Tuple of (response_dict, status_code)
        """
        response = {
            'success': False,
            'message': message
        }
        
        if include_details and error_details:
            response['data'] = {'error_details': error_details}
        
        return response, 500
    
    @staticmethod
    def created(
        data: Any,
        message: str = "Resource created successfully",
        resource_id: Any = None
    ) -> tuple:
        """
        Build a resource created success response
        
        Args:
            data: Created resource data
            message: Success message
            resource_id: ID of created resource
            
        Returns:
            Tuple of (response_dict, status_code)
        """
        if resource_id:
            message = f"{message} (ID: {resource_id})"
        
        return ResponseBuilder.success(
            data=data,
            message=message,
            status_code=201
        )
    
    @staticmethod
    def updated(
        data: Any = None,
        message: str = "Resource updated successfully"
    ) -> tuple:
        """
        Build a resource updated success response
        
        Args:
            data: Updated resource data
            message: Success message
            
        Returns:
            Tuple of (response_dict, status_code)
        """
        return ResponseBuilder.success(
            data=data,
            message=message,
            status_code=200
        )
    
    @staticmethod
    def deleted(
        message: str = "Resource deleted successfully"
    ) -> tuple:
        """
        Build a resource deleted success response
        
        Args:
            message: Success message
            
        Returns:
            Tuple of (response_dict, status_code)
        """
        return ResponseBuilder.success(
            message=message,
            status_code=200
        )
    
    @staticmethod
    def no_content() -> tuple:
        """
        Build a no content response
        
        Returns:
            Tuple of (empty_dict, status_code)
        """
        return {}, 204


# Convenience functions for quick response building
def success_response(*args, **kwargs):
    """Shorthand for ResponseBuilder.success()"""
    return ResponseBuilder.success(*args, **kwargs)


def error_response(*args, **kwargs):
    """Shorthand for ResponseBuilder.error()"""
    return ResponseBuilder.error(*args, **kwargs)


def paginated_response(*args, **kwargs):
    """Shorthand for ResponseBuilder.paginated_success()"""
    return ResponseBuilder.paginated_success(*args, **kwargs)


def validation_error_response(*args, **kwargs):
    """Shorthand for ResponseBuilder.validation_error()"""
    return ResponseBuilder.validation_error(*args, **kwargs)


def not_found_response(*args, **kwargs):
    """Shorthand for ResponseBuilder.not_found()"""
    return ResponseBuilder.not_found(*args, **kwargs)


def unauthorized_response(*args, **kwargs):
    """Shorthand for ResponseBuilder.unauthorized()"""
    return ResponseBuilder.unauthorized(*args, **kwargs)


def forbidden_response(*args, **kwargs):
    """Shorthand for ResponseBuilder.forbidden()"""
    return ResponseBuilder.forbidden(*args, **kwargs)


def created_response(*args, **kwargs):
    """Shorthand for ResponseBuilder.created()"""
    return ResponseBuilder.created(*args, **kwargs)


def updated_response(*args, **kwargs):
    """Shorthand for ResponseBuilder.updated()"""
    return ResponseBuilder.updated(*args, **kwargs)


def deleted_response(*args, **kwargs):
    """Shorthand for ResponseBuilder.deleted()"""
    return ResponseBuilder.deleted(*args, **kwargs)