"""HTTP API client for WhatsApp bridge communication."""

import requests
import logging
from typing import Optional, Dict, Any, Tuple
from pathlib import Path

from .config import config
from .models import APIResponse
from .validation import validate_recipient, validate_file_path

logger = logging.getLogger(__name__)


class APIError(Exception):
    """API communication error."""
    pass


class WhatsAppAPIClient:
    """Client for communicating with WhatsApp bridge API."""
    
    def __init__(self, base_url: str = None, timeout: int = None):
        self.base_url = base_url or config.whatsapp_api_base_url
        self.timeout = timeout or config.api_timeout
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'WhatsApp-MCP-Client/1.0'
        })
    
    def send_message(self, recipient: str, message: str) -> Tuple[bool, str]:
        """Send a text message."""
        validate_recipient(recipient)
        
        if not message.strip():
            return False, "Message content cannot be empty"
        
        payload = {
            'recipient': recipient,
            'message': message
        }
        
        try:
            response = self._post('/send', payload)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('success', False), data.get('message', 'Unknown error')
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
                
        except requests.RequestException as e:
            logger.error(f"Failed to send message: {e}")
            return False, f"Network error: {e}"
        except Exception as e:
            logger.error(f"Unexpected error sending message: {e}")
            return False, f"Unexpected error: {e}"
    
    def send_file(self, recipient: str, file_path: str) -> Tuple[bool, str]:
        """Send a file."""
        validate_recipient(recipient)
        validated_path = validate_file_path(file_path)
        
        try:
            with open(validated_path, 'rb') as f:
                files = {'file': (Path(validated_path).name, f)}
                data = {'recipient': recipient}
                
                response = self.session.post(
                    f"{self.base_url}/send",
                    data=data,
                    files=files,
                    timeout=self.timeout
                )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('success', False), data.get('message', 'Unknown error')
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
                
        except FileNotFoundError:
            return False, f"File not found: {file_path}"
        except requests.RequestException as e:
            logger.error(f"Failed to send file: {e}")
            return False, f"Network error: {e}"
        except Exception as e:
            logger.error(f"Unexpected error sending file: {e}")
            return False, f"Unexpected error: {e}"
    
    def download_media(self, message_id: str, chat_jid: str) -> Optional[str]:
        """Download media from a message."""
        if not message_id or not chat_jid:
            logger.error("Message ID and Chat JID are required for media download")
            return None
        
        payload = {
            'message_id': message_id,
            'chat_jid': chat_jid
        }
        
        try:
            response = self._post('/download', payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data.get('file_path')
                else:
                    logger.error(f"Download failed: {data.get('message', 'Unknown error')}")
                    return None
            else:
                logger.error(f"Download HTTP error {response.status_code}: {response.text}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Failed to download media: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error downloading media: {e}")
            return None
    
    def _post(self, endpoint: str, data: Dict[str, Any]) -> requests.Response:
        """Make a POST request to the API."""
        url = f"{self.base_url}{endpoint}"
        
        logger.debug(f"POST {url} with data: {data}")
        
        response = self.session.post(
            url,
            json=data,
            timeout=self.timeout
        )
        
        logger.debug(f"Response: {response.status_code} {response.text[:200]}")
        
        return response
    
    def _get(self, endpoint: str, params: Dict[str, Any] = None) -> requests.Response:
        """Make a GET request to the API."""
        url = f"{self.base_url}{endpoint}"
        
        logger.debug(f"GET {url} with params: {params}")
        
        response = self.session.get(
            url,
            params=params,
            timeout=self.timeout
        )
        
        logger.debug(f"Response: {response.status_code} {response.text[:200]}")
        
        return response
    
    def health_check(self) -> bool:
        """Check if the API is responding."""
        try:
            response = self._get('/health')
            return response.status_code == 200
        except Exception:
            return False
    
    def close(self):
        """Close the HTTP session."""
        self.session.close()


# Global API client instance
api_client = WhatsAppAPIClient()