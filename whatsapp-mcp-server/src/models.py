"""Data models for WhatsApp MCP server."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class Message:
    """Represents a WhatsApp message."""
    
    id: str
    timestamp: datetime
    sender: str
    content: str
    is_from_me: bool
    chat_jid: str
    chat_name: Optional[str] = None
    media_type: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'sender': self.sender,
            'content': self.content,
            'is_from_me': self.is_from_me,
            'chat_jid': self.chat_jid,
            'chat_name': self.chat_name,
            'media_type': self.media_type,
        }


@dataclass
class Chat:
    """Represents a WhatsApp chat."""
    
    jid: str
    name: Optional[str]
    last_message_time: Optional[datetime]
    last_message: Optional[str] = None
    last_sender: Optional[str] = None
    last_is_from_me: Optional[bool] = None
    
    @property
    def is_group(self) -> bool:
        """Determine if chat is a group based on JID pattern."""
        return self.jid.endswith("@g.us")
    
    @property
    def is_contact(self) -> bool:
        """Determine if chat is a direct contact."""
        return self.jid.endswith("@s.whatsapp.net")
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'jid': self.jid,
            'name': self.name,
            'last_message_time': self.last_message_time.isoformat() if self.last_message_time else None,
            'last_message': self.last_message,
            'last_sender': self.last_sender,
            'last_is_from_me': self.last_is_from_me,
            'is_group': self.is_group,
            'is_contact': self.is_contact,
        }


@dataclass
class Contact:
    """Represents a WhatsApp contact."""
    
    phone_number: str
    name: Optional[str]
    jid: str
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'phone_number': self.phone_number,
            'name': self.name,
            'jid': self.jid,
        }


@dataclass
class MessageContext:
    """Represents a message with surrounding context."""
    
    message: Message
    before: List[Message]
    after: List[Message]
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'message': self.message.to_dict(),
            'before': [msg.to_dict() for msg in self.before],
            'after': [msg.to_dict() for msg in self.after],
        }


@dataclass
class APIResponse:
    """Standard API response format."""
    
    success: bool
    message: Optional[str] = None
    data: Optional[dict] = None
    error: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {'success': self.success}
        if self.message:
            result['message'] = self.message
        if self.data:
            result['data'] = self.data
        if self.error:
            result['error'] = self.error
        return result