"""Tests for validation module."""

import pytest
import tempfile
import os
from datetime import datetime
from pathlib import Path

from src.validation import (
    ValidationError,
    validate_phone_number,
    validate_jid,
    validate_recipient,
    validate_message_content,
    validate_file_path,
    validate_date_string,
    validate_pagination_params,
    validate_context_params,
    sanitize_search_query
)


class TestPhoneValidation:
    """Test phone number validation."""
    
    def test_valid_phone_numbers(self):
        """Test valid phone numbers."""
        valid_phones = ["1234567890", "123456789012345"]
        for phone in valid_phones:
            validate_phone_number(phone)  # Should not raise
    
    def test_invalid_phone_numbers(self):
        """Test invalid phone numbers."""
        invalid_phones = ["", "123", "12345678901234567890", "abc123", "123-456-7890"]
        for phone in invalid_phones:
            with pytest.raises(ValidationError):
                validate_phone_number(phone)


class TestJIDValidation:
    """Test JID validation."""
    
    def test_valid_jids(self):
        """Test valid JIDs."""
        valid_jids = [
            "1234567890@s.whatsapp.net",
            "123456789-123456789@g.us"
        ]
        for jid in valid_jids:
            validate_jid(jid)  # Should not raise
    
    def test_invalid_jids(self):
        """Test invalid JIDs."""
        invalid_jids = ["", "invalid", "123@invalid.domain", "123456789@invalid"]
        for jid in invalid_jids:
            with pytest.raises(ValidationError):
                validate_jid(jid)


class TestRecipientValidation:
    """Test recipient validation."""
    
    def test_valid_recipients(self):
        """Test valid recipients."""
        valid_recipients = [
            "1234567890",
            "1234567890@s.whatsapp.net",
            "123456789-123456789@g.us"
        ]
        for recipient in valid_recipients:
            validate_recipient(recipient)  # Should not raise
    
    def test_invalid_recipients(self):
        """Test invalid recipients."""
        invalid_recipients = ["", "invalid", "123@invalid.domain"]
        for recipient in invalid_recipients:
            with pytest.raises(ValidationError):
                validate_recipient(recipient)


class TestMessageContentValidation:
    """Test message content validation."""
    
    def test_valid_content(self):
        """Test valid message content."""
        validate_message_content("Hello, world!")  # Should not raise
    
    def test_empty_content(self):
        """Test empty message content."""
        with pytest.raises(ValidationError):
            validate_message_content("")
    
    def test_too_long_content(self):
        """Test message content that's too long."""
        long_content = "x" * 5000
        with pytest.raises(ValidationError):
            validate_message_content(long_content)


class TestFilePathValidation:
    """Test file path validation."""
    
    def test_valid_file_path(self):
        """Test valid file path."""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b"test content")
            temp_path = f.name
        
        try:
            result = validate_file_path(temp_path)
            assert result == str(Path(temp_path).resolve())
        finally:
            os.unlink(temp_path)
    
    def test_nonexistent_file(self):
        """Test nonexistent file path."""
        with pytest.raises(ValidationError):
            validate_file_path("/nonexistent/file.txt")
    
    def test_empty_path(self):
        """Test empty file path."""
        with pytest.raises(ValidationError):
            validate_file_path("")
    
    def test_directory_path(self):
        """Test directory path (should fail)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(ValidationError):
                validate_file_path(temp_dir)
    
    def test_unsupported_file_type(self):
        """Test unsupported file type."""
        with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as f:
            temp_path = f.name
        
        try:
            with pytest.raises(ValidationError):
                validate_file_path(temp_path)
        finally:
            os.unlink(temp_path)


class TestDateStringValidation:
    """Test date string validation."""
    
    def test_valid_date_strings(self):
        """Test valid ISO date strings."""
        valid_dates = [
            "2023-01-01T00:00:00",
            "2023-12-31T23:59:59",
            "2023-06-15T12:30:45"
        ]
        for date_str in valid_dates:
            result = validate_date_string(date_str)
            assert isinstance(result, datetime)
    
    def test_invalid_date_strings(self):
        """Test invalid date strings."""
        invalid_dates = ["", "invalid", "2023-13-01T00:00:00", "2023-01-32T00:00:00"]
        for date_str in invalid_dates:
            with pytest.raises(ValidationError):
                validate_date_string(date_str)


class TestPaginationValidation:
    """Test pagination parameters validation."""
    
    def test_valid_pagination(self):
        """Test valid pagination parameters."""
        limit, offset = validate_pagination_params(20, 2)
        assert limit == 20
        assert offset == 40
    
    def test_invalid_limit(self):
        """Test invalid limit values."""
        with pytest.raises(ValidationError):
            validate_pagination_params(0, 0)
        
        with pytest.raises(ValidationError):
            validate_pagination_params(101, 0)
    
    def test_invalid_page(self):
        """Test invalid page values."""
        with pytest.raises(ValidationError):
            validate_pagination_params(20, -1)


class TestContextValidation:
    """Test context parameters validation."""
    
    def test_valid_context(self):
        """Test valid context parameters."""
        before, after = validate_context_params(5, 10)
        assert before == 5
        assert after == 10
    
    def test_invalid_context(self):
        """Test invalid context parameters."""
        with pytest.raises(ValidationError):
            validate_context_params(-1, 5)
        
        with pytest.raises(ValidationError):
            validate_context_params(5, 51)


class TestSearchQuerySanitization:
    """Test search query sanitization."""
    
    def test_clean_query(self):
        """Test clean search query."""
        result = sanitize_search_query("hello world")
        assert result == "hello world"
    
    def test_malicious_query(self):
        """Test malicious search query."""
        malicious = "'; DROP TABLE messages; --"
        result = sanitize_search_query(malicious)
        assert "''" in result  # Single quotes should be escaped
        assert "--" not in result  # Comments should be removed
        assert ";" not in result  # Semicolons should be removed
    
    def test_empty_query(self):
        """Test empty search query."""
        result = sanitize_search_query("")
        assert result == ""
    
    def test_long_query(self):
        """Test very long search query."""
        long_query = "x" * 200
        result = sanitize_search_query(long_query)
        assert len(result) <= 100