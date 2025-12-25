"""
API Client for Telegram Bot
Handles HTTP requests to API endpoints from the bot
"""
import requests
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import urllib3

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

class BotAPIClient:
    """Client for making requests to API from bot"""
    
    def __init__(self):
        self.base_url = os.getenv('API_BASE_URL', 'http://localhost:5001')
        self.api_prefix = '/api/v1'
        print(f"🔗 Bot API Client initialized")
        print(f"📍 Base URL: {self.base_url}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response"""
        try:
            data = response.json()
            if response.status_code >= 400:
                print(f"❌ API Error {response.status_code}: {data.get('message', 'Unknown error')}")
            else:
                print(f"API Success {response.status_code}")
            return data
        except Exception as e:
            print(f"❌ Failed to parse response: {str(e)}")
            print(f"📄 Raw response: {response.text[:200]}")
            return {
                'success': False,
                'message': f'Failed to parse response: {str(e)}',
                'data': None
            }
    
    def get(self, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        """Make GET request"""
        try:
            url = f"{self.base_url}{self.api_prefix}{endpoint}"
            print(f"📡 GET {url}")
            
            # For HTTPS with self-signed cert, disable SSL verification
            verify_ssl = False if self.base_url.startswith('https://') else True
            
            response = requests.get(
                url, 
                params=params, 
                headers=self._get_headers(), 
                timeout=10,
                verify=verify_ssl
            )
            return self._handle_response(response)
            
        except requests.exceptions.ConnectionError as e:
            error_msg = f"❌ Connection failed to {self.base_url}"
            print(error_msg)
            print(f"   Error details: {str(e)}")
            print(f"   💡 Troubleshooting:")
            print(f"      - Check if API is running: curl -k {self.base_url}/health")
            print(f"      - Check if Apache is running: sudo systemctl status apache2")
            print(f"      - Check hosts file: cat /etc/hosts | grep chatbot.ibs.local")
            return {'success': False, 'message': 'API connection failed', 'data': None}
            
        except requests.exceptions.Timeout as e:
            error_msg = f"❌ Request timeout to {self.base_url}"
            print(error_msg)
            return {'success': False, 'message': 'API request timeout', 'data': None}
            
        except requests.exceptions.SSLError as e:
            error_msg = f"❌ SSL/Certificate error for {self.base_url}"
            print(error_msg)
            print(f"   Error details: {str(e)}")
            print(f"   💡 Try: curl -k {self.base_url}/health")
            return {'success': False, 'message': 'SSL certificate error', 'data': None}
            
        except Exception as e:
            error_msg = f"❌ Unexpected error: {str(e)}"
            print(error_msg)
            return {'success': False, 'message': str(e), 'data': None}
    
    def post(self, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """Make POST request"""
        try:
            url = f"{self.base_url}{self.api_prefix}{endpoint}"
            print(f"📡 POST {url}")
            
            # For HTTPS with self-signed cert, disable SSL verification
            verify_ssl = False if self.base_url.startswith('https://') else True
            
            response = requests.post(
                url, 
                json=data, 
                headers=self._get_headers(), 
                timeout=10,
                verify=verify_ssl
            )
            return self._handle_response(response)
            
        except requests.exceptions.ConnectionError as e:
            error_msg = f"❌ Connection failed to {self.base_url}"
            print(error_msg)
            print(f"   Error details: {str(e)}")
            print(f"   💡 Troubleshooting:")
            print(f"      - Check if API is running: curl -k {self.base_url}/health")
            print(f"      - Check if Apache is running: sudo systemctl status apache2")
            print(f"      - Check hosts file: cat /etc/hosts | grep chatbot.ibs.local")
            return {'success': False, 'message': 'API connection failed', 'data': None}
            
        except requests.exceptions.Timeout as e:
            error_msg = f"❌ Request timeout to {self.base_url}"
            print(error_msg)
            return {'success': False, 'message': 'API request timeout', 'data': None}
            
        except requests.exceptions.SSLError as e:
            error_msg = f"❌ SSL/Certificate error for {self.base_url}"
            print(error_msg)
            print(f"   Error details: {str(e)}")
            print(f"   💡 Try: curl -k {self.base_url}/health")
            return {'success': False, 'message': 'SSL certificate error', 'data': None}
            
        except Exception as e:
            error_msg = f"❌ Unexpected error: {str(e)}"
            print(error_msg)
            return {'success': False, 'message': str(e), 'data': None}
    
    def put(self, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """Make PUT request"""
        try:
            url = f"{self.base_url}{self.api_prefix}{endpoint}"
            print(f"📡 PUT {url}")
            
            # For HTTPS with self-signed cert, disable SSL verification
            verify_ssl = False if self.base_url.startswith('https://') else True
            
            response = requests.put(
                url, 
                json=data, 
                headers=self._get_headers(), 
                timeout=10,
                verify=verify_ssl
            )
            return self._handle_response(response)
            
        except requests.exceptions.ConnectionError as e:
            error_msg = f"❌ Connection failed to {self.base_url}"
            print(error_msg)
            print(f"   Error details: {str(e)}")
            print(f"   💡 Troubleshooting:")
            print(f"      - Check if API is running: curl -k {self.base_url}/health")
            print(f"      - Check if Apache is running: sudo systemctl status apache2")
            print(f"      - Check hosts file: cat /etc/hosts | grep chatbot.ibs.local")
            return {'success': False, 'message': 'API connection failed', 'data': None}
            
        except requests.exceptions.Timeout as e:
            error_msg = f"❌ Request timeout to {self.base_url}"
            print(error_msg)
            return {'success': False, 'message': 'API request timeout', 'data': None}
            
        except requests.exceptions.SSLError as e:
            error_msg = f"❌ SSL/Certificate error for {self.base_url}"
            print(error_msg)
            print(f"   Error details: {str(e)}")
            print(f"   💡 Try: curl -k {self.base_url}/health")
            return {'success': False, 'message': 'SSL certificate error', 'data': None}
            
        except Exception as e:
            error_msg = f"❌ Unexpected error: {str(e)}"
            print(error_msg)
            return {'success': False, 'message': str(e), 'data': None}

# Global instance
bot_api_client = BotAPIClient()