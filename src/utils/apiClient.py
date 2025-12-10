"""
API Client for Web Application
Handles HTTP requests to our own API endpoints
"""

import requests
import os
from flask import session, current_app
from typing import Dict, Any, Optional
import urllib3

# ⚠️ Disable SSL warnings for development
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class APIClient:
    """Client for making requests to our own API"""
    
    def __init__(self):
        self.base_url = os.getenv('API_BASE_URL', 'https://chatbot.ibs.local')
        self.timeout = 30
        #  Disable SSL verification for local development
        self.verify_ssl = os.getenv('API_SSL_VERIFY', 'false').lower() == 'true'
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with JWT token from session"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        access_token = session.get('access_token')
        if access_token:
            headers['Authorization'] = f'Bearer {access_token}'
        
        return headers
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and convert to dict"""
        try:
            data = response.json()
            
            #  Convert ISO date strings to datetime objects if needed
            if data.get('success') and 'data' in data:
                self._convert_dates_in_data(data['data'])
            
        except ValueError:
            data = {'success': False, 'message': 'Invalid JSON response'}
    
        if response.status_code == 401:
            session.clear()
            data['redirect_to_login'] = True
    
        return data
    
    def _convert_dates_in_data(self, data):
        """Convert ISO date strings to datetime objects recursively"""
        from datetime import datetime
        
        if isinstance(data, dict):
            for key, value in data.items():
                if key in ['created_at', 'updated_at', 'last_login', 'registration_date', 'last_activity']:
                    if isinstance(value, str) and value:
                        try:
                            # Parse ISO format dates
                            data[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                        except:
                            pass  # Keep as string if parsing fails
                elif isinstance(value, (dict, list)):
                    self._convert_dates_in_data(value)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    self._convert_dates_in_data(item)
    
    def get(self, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        """Make GET request to API"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.get(
                url, 
                headers=self._get_headers(),
                params=params or {},
                timeout=self.timeout,
                verify=self.verify_ssl  #  Use SSL verification setting
            )
            return self._handle_response(response)
        except requests.RequestException as e:
            current_app.logger.error(f"API GET request failed: {e}")
            return {'success': False, 'message': f'Network error: {str(e)}'}
    
    def post(self, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """Make POST request to API"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=data or {},
                timeout=self.timeout,
                verify=self.verify_ssl  #  Use SSL verification setting
            )
            return self._handle_response(response)
        except requests.RequestException as e:
            current_app.logger.error(f"API POST request failed: {e}")
            return {'success': False, 'message': f'Network error: {str(e)}'}
    
    def put(self, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """Make PUT request to API"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.put(
                url,
                headers=self._get_headers(),
                json=data or {},
                timeout=self.timeout,
                verify=self.verify_ssl  #  Use SSL verification setting
            )
            return self._handle_response(response)
        except requests.RequestException as e:
            current_app.logger.error(f"API PUT request failed: {e}")
            return {'success': False, 'message': f'Network error: {str(e)}'}
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make DELETE request to API"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.delete(
                url,
                headers=self._get_headers(),
                timeout=self.timeout,
                verify=self.verify_ssl  #  Use SSL verification setting
            )
            return self._handle_response(response)
        except requests.RequestException as e:
            current_app.logger.error(f"API DELETE request failed: {e}")
            return {'success': False, 'message': f'Network error: {str(e)}'}

# Global instance
api_client = APIClient()