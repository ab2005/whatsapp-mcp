"""Input validation utilities for WhatsApp MCP server."""

import re
import os
from pathlib import Path
from typing import Optional
from datetime import datetime

from .config import config


class ValidationError(Exception):
    """Validation error."""
    pass


# Regex patterns for validation
PHONE_PATTERN = re.compile(r'^\d{10,15}$')
JID_PHONE_PATTERN = re.compile(r'^\d{10,15}@s\.whatsapp\.net$')
JID_GROUP_PATTERN = re.compile(r'^\d+-\d+@g\.us$')
DATE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}')


def validate_phone_number(phone: str) -> None:
    """Validate phone number format."""
    if not phone:
        raise ValidationError("Phone number cannot be empty")
    
    if not PHONE_PATTERN.match(phone):
        raise ValidationError(f"Invalid phone number format: {phone} (should be 10-15 digits)")


def validate_jid(jid: str) -> None:
    """Validate WhatsApp JID format."""
    if not jid:
        raise ValidationError("JID cannot be empty")
    
    if not (JID_PHONE_PATTERN.match(jid) or JID_GROUP_PATTERN.match(jid)):
        raise ValidationError(f"Invalid JID format: {jid}")


def validate_recipient(recipient: str) -> None:
    """Validate recipient (can be phone number or JID)."""
    if not recipient:
        raise ValidationError("Recipient cannot be empty")
    
    try:
        # Try phone number first
        validate_phone_number(recipient)
        return
    except ValidationError:
        pass
    
    try:
        # Try JID format
        validate_jid(recipient)
        return
    except ValidationError:
        pass
    
    raise ValidationError(f"Invalid recipient format: {recipient}")


def validate_message_content(content: str) -> None:
    """Validate message content."""
    if not content:
        raise ValidationError("Message content cannot be empty")
    
    if len(content) > config.max_message_length:
        raise ValidationError(
            f"Message too long: {len(content)} characters (max {config.max_message_length})"
        )


def validate_file_path(file_path: str) -> str:
    """Validate and sanitize file path."""
    if not file_path:
        raise ValidationError("File path cannot be empty")
    
    try:
        # Convert to Path object for better handling
        path = Path(file_path).resolve()
        
        # Check if file exists
        if not path.exists():
            raise ValidationError(f"File does not exist: {file_path}")
        
        # Check if it's a file (not directory)
        if not path.is_file():
            raise ValidationError(f"Path is not a file: {file_path}")
        
        # Check file size
        file_size = path.stat().st_size
        if file_size > config.max_file_size:
            raise ValidationError(
                f"File too large: {file_size} bytes (max {config.max_file_size})"
            )
        
        # Validate file extension
        file_ext = path.suffix.lower().lstrip('.')
        if file_ext not in config.allowed_file_types:
            raise ValidationError(
                f"Unsupported file type: {file_ext} (allowed: {', '.join(config.allowed_file_types)})"
            )
        
        return str(path)
        
    except OSError as e:
        raise ValidationError(f"Invalid file path: {e}")


def validate_date_string(date_str: str) -> datetime:
    """Validate and parse ISO date string."""
    if not date_str:
        raise ValidationError("Date string cannot be empty")
    
    if not DATE_PATTERN.match(date_str):
        raise ValidationError(f"Invalid date format: {date_str} (expected ISO format)")
    
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except ValueError as e:
        raise ValidationError(f"Invalid date: {e}")


def validate_pagination_params(limit: int, page: int) -> tuple[int, int]:
    """Validate pagination parameters."""
    if limit < 1 or limit > 100:
        raise ValidationError("Limit must be between 1 and 100")
    
    if page < 0:
        raise ValidationError("Page must be non-negative")
    
    offset = page * limit
    return limit, offset


def validate_context_params(before: int, after: int) -> tuple[int, int]:
    """Validate context parameters."""
    if before < 0 or before > 50:
        raise ValidationError("Before context must be between 0 and 50")
    
    if after < 0 or after > 50:
        raise ValidationError("After context must be between 0 and 50")
    
    return before, after


def sanitize_search_query(query: str) -> str:
    """Sanitize search query to prevent SQL injection."""
    if not query:
        return ""
    
    # Remove or escape potentially dangerous characters
    # This is a basic sanitization - for production, use parameterized queries
    sanitized = query.replace("'", "''").replace(";", "").replace("--", "")
    
    # Limit query length
    if len(sanitized) > 100:
        sanitized = sanitized[:100]
    
    return sanitized.strip()