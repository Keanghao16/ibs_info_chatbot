"""
JWT Helper Utilities
Provides JWT token generation, validation, and decoding functions
"""

import jwt
import os
from datetime import datetime, timedelta
from typing import Dict, Optional

class JWTHelper:
    """Helper class for JWT operations"""
    
    def __init__(self):
        self.secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-jwt-key-change-this-in-production')
        self.algorithm = os.getenv('JWT_ALGORITHM', 'HS256')
        self.access_token_expires = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))  # 1 hour
        self.refresh_token_expires = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 604800))  # 7 days
    
    def generate_access_token(self, admin_id: str, role: str, additional_claims: Optional[Dict] = None) -> str:
        """
        Generate JWT access token
        
        Args:
            admin_id: Admin ID
            role: Admin role (admin or super_admin)
            additional_claims: Additional claims to include in token
            
        Returns:
            JWT token string
        """
        payload = {
            'admin_id': admin_id,
            'role': role,
            'token_type': 'access',
            'exp': datetime.utcnow() + timedelta(seconds=self.access_token_expires),
            'iat': datetime.utcnow()
        }
        
        # Add additional claims if provided
        if additional_claims:
            payload.update(additional_claims)
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def generate_refresh_token(self, admin_id: str) -> str:
        """
        Generate JWT refresh token
        
        Args:
            admin_id: Admin ID
            
        Returns:
            JWT refresh token string
        """
        payload = {
            'admin_id': admin_id,
            'token_type': 'refresh',
            'exp': datetime.utcnow() + timedelta(seconds=self.refresh_token_expires),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def verify_token(self, token: str) -> Dict:
        """
        Verify and decode JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            Dictionary with success status and payload or error message
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return {
                'success': True,
                'payload': payload
            }
        except jwt.ExpiredSignatureError:
            return {
                'success': False,
                'error': 'token_expired',
                'message': 'Token has expired'
            }
        except jwt.InvalidTokenError:
            return {
                'success': False,
                'error': 'invalid_token',
                'message': 'Invalid token'
            }
        except Exception as e:
            return {
                'success': False,
                'error': 'token_error',
                'message': str(e)
            }
    
    def decode_token(self, token: str) -> Optional[Dict]:
        """
        Decode token without verification (use with caution)
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded payload or None
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm], options={'verify_signature': False})
            return payload
        except Exception:
            return None
    
    def extract_token_from_header(self, auth_header: str) -> Optional[str]:
        """
        Extract token from Authorization header
        
        Args:
            auth_header: Authorization header value
            
        Returns:
            Token string or None
        """
        if not auth_header:
            return None
        
        # Expected format: "Bearer <token>"
        parts = auth_header.split()
        
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return None
        
        return parts[1]


# Create singleton instance
jwt_helper = JWTHelper()