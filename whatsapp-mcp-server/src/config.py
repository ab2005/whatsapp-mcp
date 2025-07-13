"""Configuration management for WhatsApp MCP server."""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Application configuration."""
    
    # Database settings
    database_path: str
    
    # API settings
    whatsapp_api_base_url: str
    api_timeout: int
    
    # File settings
    media_storage_path: str
    max_file_size: int
    
    # Logging settings
    log_level: str
    
    # Security settings
    max_message_length: int
    allowed_file_types: list[str]


def load_config() -> Config:
    """Load configuration from environment variables with defaults."""
    
    # Base paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    bridge_dir = os.path.join(os.path.dirname(base_dir), 'whatsapp-bridge')
    
    return Config(
        # Database
        database_path=os.getenv(
            'WHATSAPP_DB_PATH',
            os.path.join(bridge_dir, 'store', 'messages.db')
        ),
        
        # API
        whatsapp_api_base_url=os.getenv(
            'WHATSAPP_API_BASE_URL',
            'http://localhost:8080/api'
        ),
        api_timeout=int(os.getenv('WHATSAPP_API_TIMEOUT', '30')),
        
        # Files
        media_storage_path=os.getenv(
            'WHATSAPP_MEDIA_PATH',
            os.path.join(bridge_dir, 'store', 'media')
        ),
        max_file_size=int(os.getenv('WHATSAPP_MAX_FILE_SIZE', '100000000')),  # 100MB
        
        # Logging
        log_level=os.getenv('WHATSAPP_LOG_LEVEL', 'INFO'),
        
        # Security
        max_message_length=int(os.getenv('WHATSAPP_MAX_MESSAGE_LENGTH', '4096')),
        allowed_file_types=os.getenv(
            'WHATSAPP_ALLOWED_FILE_TYPES',
            'jpg,jpeg,png,gif,webp,mp4,mov,avi,mp3,wav,ogg,m4a,pdf,doc,docx,txt'
        ).split(','),
    )


# Global config instance
config = load_config()