"""Tests for models module."""

import pytest
from datetime import datetime

from src.models import Message, Chat, Contact, MessageContext, APIResponse


class TestMessage:
    """Test Message model."""
    
    def test_message_creation(self):
        """Test message creation."""
        timestamp = datetime.now()
        message = Message(
            id="msg123",
            timestamp=timestamp,
            sender="1234567890@s.whatsapp.net",
            content="Hello, world!",
            is_from_me=False,
            chat_jid="1234567890@s.whatsapp.net",
            chat_name="Test Contact",
            media_type=None
        )
        
        assert message.id == "msg123"
        assert message.timestamp == timestamp
        assert message.sender == "1234567890@s.whatsapp.net"
        assert message.content == "Hello, world!"
        assert message.is_from_me is False
        assert message.chat_jid == "1234567890@s.whatsapp.net"
        assert message.chat_name == "Test Contact"
        assert message.media_type is None
    
    def test_message_to_dict(self):
        """Test message to dictionary conversion."""
        timestamp = datetime(2023, 1, 1, 12, 0, 0)
        message = Message(
            id="msg123",
            timestamp=timestamp,
            sender="1234567890@s.whatsapp.net",
            content="Hello, world!",
            is_from_me=False,
            chat_jid="1234567890@s.whatsapp.net",
            chat_name="Test Contact",
            media_type="image"
        )
        
        result = message.to_dict()
        expected = {
            'id': "msg123",
            'timestamp': "2023-01-01T12:00:00",
            'sender': "1234567890@s.whatsapp.net",
            'content': "Hello, world!",
            'is_from_me': False,
            'chat_jid': "1234567890@s.whatsapp.net",
            'chat_name': "Test Contact",
            'media_type': "image",
        }
        
        assert result == expected


class TestChat:
    """Test Chat model."""
    
    def test_chat_creation(self):
        """Test chat creation."""
        timestamp = datetime.now()
        chat = Chat(
            jid="1234567890@s.whatsapp.net",
            name="Test Contact",
            last_message_time=timestamp,
            last_message="Hello",
            last_sender="1234567890@s.whatsapp.net",
            last_is_from_me=False
        )
        
        assert chat.jid == "1234567890@s.whatsapp.net"
        assert chat.name == "Test Contact"
        assert chat.last_message_time == timestamp
        assert chat.last_message == "Hello"
        assert chat.last_sender == "1234567890@s.whatsapp.net"
        assert chat.last_is_from_me is False
    
    def test_is_group_property(self):
        """Test is_group property."""
        # Contact chat
        contact_chat = Chat(
            jid="1234567890@s.whatsapp.net",
            name="Contact",
            last_message_time=None
        )
        assert contact_chat.is_group is False
        
        # Group chat
        group_chat = Chat(
            jid="123456789-123456789@g.us",
            name="Group",
            last_message_time=None
        )
        assert group_chat.is_group is True
    
    def test_is_contact_property(self):
        """Test is_contact property."""
        # Contact chat
        contact_chat = Chat(
            jid="1234567890@s.whatsapp.net",
            name="Contact",
            last_message_time=None
        )
        assert contact_chat.is_contact is True
        
        # Group chat
        group_chat = Chat(
            jid="123456789-123456789@g.us",
            name="Group",
            last_message_time=None
        )
        assert group_chat.is_contact is False
    
    def test_chat_to_dict(self):
        """Test chat to dictionary conversion."""
        timestamp = datetime(2023, 1, 1, 12, 0, 0)
        chat = Chat(
            jid="1234567890@s.whatsapp.net",
            name="Test Contact",
            last_message_time=timestamp,
            last_message="Hello",
            last_sender="1234567890@s.whatsapp.net",
            last_is_from_me=False
        )
        
        result = chat.to_dict()
        expected = {
            'jid': "1234567890@s.whatsapp.net",
            'name': "Test Contact",
            'last_message_time': "2023-01-01T12:00:00",
            'last_message': "Hello",
            'last_sender': "1234567890@s.whatsapp.net",
            'last_is_from_me': False,
            'is_group': False,
            'is_contact': True,
        }
        
        assert result == expected


class TestContact:
    """Test Contact model."""
    
    def test_contact_creation(self):
        """Test contact creation."""
        contact = Contact(
            phone_number="1234567890",
            name="Test Contact",
            jid="1234567890@s.whatsapp.net"
        )
        
        assert contact.phone_number == "1234567890"
        assert contact.name == "Test Contact"
        assert contact.jid == "1234567890@s.whatsapp.net"
    
    def test_contact_to_dict(self):
        """Test contact to dictionary conversion."""
        contact = Contact(
            phone_number="1234567890",
            name="Test Contact",
            jid="1234567890@s.whatsapp.net"
        )
        
        result = contact.to_dict()
        expected = {
            'phone_number': "1234567890",
            'name': "Test Contact",
            'jid': "1234567890@s.whatsapp.net",
        }
        
        assert result == expected


class TestMessageContext:
    """Test MessageContext model."""
    
    def test_message_context_creation(self):
        """Test message context creation."""
        timestamp = datetime.now()
        
        target_message = Message(
            id="msg2",
            timestamp=timestamp,
            sender="sender",
            content="Target message",
            is_from_me=False,
            chat_jid="chat123"
        )
        
        before_messages = [
            Message(
                id="msg1",
                timestamp=timestamp,
                sender="sender",
                content="Before message",
                is_from_me=False,
                chat_jid="chat123"
            )
        ]
        
        after_messages = [
            Message(
                id="msg3",
                timestamp=timestamp,
                sender="sender",
                content="After message",
                is_from_me=False,
                chat_jid="chat123"
            )
        ]
        
        context = MessageContext(
            message=target_message,
            before=before_messages,
            after=after_messages
        )
        
        assert context.message == target_message
        assert context.before == before_messages
        assert context.after == after_messages
    
    def test_message_context_to_dict(self):
        """Test message context to dictionary conversion."""
        timestamp = datetime(2023, 1, 1, 12, 0, 0)
        
        target_message = Message(
            id="msg2",
            timestamp=timestamp,
            sender="sender",
            content="Target message",
            is_from_me=False,
            chat_jid="chat123"
        )
        
        context = MessageContext(
            message=target_message,
            before=[],
            after=[]
        )
        
        result = context.to_dict()
        
        assert 'message' in result
        assert 'before' in result
        assert 'after' in result
        assert result['message']['id'] == "msg2"
        assert result['before'] == []
        assert result['after'] == []


class TestAPIResponse:
    """Test APIResponse model."""
    
    def test_success_response(self):
        """Test successful API response."""
        response = APIResponse(
            success=True,
            message="Operation successful",
            data={"key": "value"}
        )
        
        result = response.to_dict()
        expected = {
            'success': True,
            'message': "Operation successful",
            'data': {"key": "value"}
        }
        
        assert result == expected
    
    def test_error_response(self):
        """Test error API response."""
        response = APIResponse(
            success=False,
            error="Something went wrong"
        )
        
        result = response.to_dict()
        expected = {
            'success': False,
            'error': "Something went wrong"
        }
        
        assert result == expected
    
    def test_minimal_response(self):
        """Test minimal API response."""
        response = APIResponse(success=True)
        
        result = response.to_dict()
        expected = {'success': True}
        
        assert result == expected