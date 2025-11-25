"""
CORS Middleware Configuration
Handles Cross-Origin Resource Sharing (CORS) for API endpoints
"""

import os
from flask_cors import CORS

class CORSConfig:
    """CORS configuration settings"""
    
    def __init__(self):
        # Get allowed origins from environment or use defaults
        self.allowed_origins = self._parse_origins(
            os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173,http://localhost:5000')
        )
        
        # Get allowed methods from environment or use defaults
        self.allowed_methods = self._parse_methods(
            os.getenv('CORS_METHODS', 'GET,POST,PUT,DELETE,OPTIONS')
        )
        
        # Standard allowed headers
        self.allowed_headers = [
            'Content-Type',
            'Authorization',
            'X-Requested-With',
            'Accept',
            'Origin',
            'Access-Control-Request-Method',
            'Access-Control-Request-Headers'
        ]
        
        # Headers to expose to the client
        self.exposed_headers = [
            'Content-Range',
            'X-Content-Range',
            'X-Total-Count',
            'X-API-Version'
        ]
        
        # Enable credentials (cookies, authorization headers)
        self.supports_credentials = True
        
        # Preflight request cache duration (in seconds)
        self.max_age = 3600  # 1 hour
    
    def _parse_origins(self, origins_str: str) -> list:
        """
        Parse comma-separated origins string into list
        
        Args:
            origins_str: Comma-separated origins string
            
        Returns:
            List of origin URLs
        """
        if not origins_str:
            return ['*']  # Allow all origins if none specified
        
        origins = [origin.strip() for origin in origins_str.split(',')]
        return [origin for origin in origins if origin]  # Remove empty strings
    
    def _parse_methods(self, methods_str: str) -> list:
        """
        Parse comma-separated methods string into list
        
        Args:
            methods_str: Comma-separated HTTP methods string
            
        Returns:
            List of HTTP methods
        """
        if not methods_str:
            return ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
        
        methods = [method.strip().upper() for method in methods_str.split(',')]
        return [method for method in methods if method]  # Remove empty strings
    
    def get_config(self) -> dict:
        """
        Get CORS configuration as dictionary
        
        Returns:
            Dictionary with CORS configuration
        """
        return {
            'origins': self.allowed_origins,
            'methods': self.allowed_methods,
            'allow_headers': self.allowed_headers,
            'expose_headers': self.exposed_headers,
            'supports_credentials': self.supports_credentials,
            'max_age': self.max_age
        }


def configure_cors(app):
    """
    Configure CORS for Flask application
    
    Args:
        app: Flask application instance
        
    Returns:
        CORS instance
    """
    # Create CORS configuration
    cors_config = CORSConfig()
    
    # Apply CORS to API routes
    cors = CORS(app, resources={
        r"/api/*": cors_config.get_config(),
        r"/health": {  # Allow health check from anywhere
            'origins': '*',
            'methods': ['GET']
        }
    })
    
    # Log CORS configuration
    print(f"\n{'='*60}")
    print("🌐 CORS Configuration")
    print(f"{'='*60}")
    print(f"📍 Allowed Origins: {', '.join(cors_config.allowed_origins)}")
    print(f"🔧 Allowed Methods: {', '.join(cors_config.allowed_methods)}")
    print(f"🔑 Supports Credentials: {cors_config.supports_credentials}")
    print(f"⏱️  Max Age: {cors_config.max_age}s")
    print(f"{'='*60}\n")
    
    return cors


def add_cors_headers(response):
    """
    Manually add CORS headers to response (fallback method)
    Use this if Flask-CORS doesn't work for specific cases
    
    Args:
        response: Flask response object
        
    Returns:
        Response with CORS headers
    """
    cors_config = CORSConfig()
    
    # Get origin from request
    origin = response.headers.get('Origin')
    
    # Check if origin is allowed
    if origin in cors_config.allowed_origins or '*' in cors_config.allowed_origins:
        response.headers['Access-Control-Allow-Origin'] = origin
    
    # Add other CORS headers
    response.headers['Access-Control-Allow-Methods'] = ', '.join(cors_config.allowed_methods)
    response.headers['Access-Control-Allow-Headers'] = ', '.join(cors_config.allowed_headers)
    response.headers['Access-Control-Expose-Headers'] = ', '.join(cors_config.exposed_headers)
    response.headers['Access-Control-Allow-Credentials'] = str(cors_config.supports_credentials).lower()
    response.headers['Access-Control-Max-Age'] = str(cors_config.max_age)
    
    return response


# Create singleton instance for easy import
cors_config = CORSConfig()