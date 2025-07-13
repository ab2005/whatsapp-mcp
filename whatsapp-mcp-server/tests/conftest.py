"""Pytest configuration and fixtures."""

import pytest
import tempfile
import sqlite3
import os
from datetime import datetime
from pathlib import Path

from src.database import DatabaseManager
from src.models import Message, Chat


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    # Initialize database schema
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE chats (
            jid TEXT PRIMARY KEY,
            name TEXT,
            last_message_time TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE messages (
            id TEXT,
            chat_jid TEXT,
            sender TEXT,
            content TEXT,
            timestamp TIMESTAMP,
            is_from_me BOOLEAN,
            media_type TEXT,
            filename TEXT,
            url TEXT,
            media_key BLOB,
            file_sha256 BLOB,
            file_enc_sha256 BLOB,
            file_length INTEGER,
            PRIMARY KEY (id, chat_jid),
            FOREIGN KEY (chat_jid) REFERENCES chats(jid)
        )
    """)
    conn.commit()
    conn.close()
    
    yield db_path
    
    # Cleanup
    os.unlink(db_path)


@pytest.fixture
def db_manager(temp_db):
    """Create a database manager for testing."""
    return DatabaseManager(temp_db)


@pytest.fixture
def sample_chat():
    """Create a sample chat for testing."""
    return Chat(
        jid="1234567890@s.whatsapp.net",
        name="Test Contact",
        last_message_time=datetime.now()
    )


@pytest.fixture
def sample_message():
    """Create a sample message for testing."""
    return Message(
        id="msg123",
        timestamp=datetime.now(),
        sender="1234567890@s.whatsapp.net",
        content="Test message",
        is_from_me=False,
        chat_jid="1234567890@s.whatsapp.net",
        chat_name="Test Contact"
    )


@pytest.fixture
def sample_group_chat():
    """Create a sample group chat for testing."""
    return Chat(
        jid="123456789-123456789@g.us",
        name="Test Group",
        last_message_time=datetime.now()
    )


@pytest.fixture
def temp_file():
    """Create a temporary file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
        f.write(b"test content")
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def temp_media_file():
    """Create a temporary media file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
        # Create a minimal JPEG header
        f.write(b'\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01')
        f.write(b'test image content')
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)