# WhatsApp MCP Tools Documentation

This document describes all the Model Context Protocol (MCP) tools available in the WhatsApp MCP server.

## Overview

The WhatsApp MCP server provides 15 tools that enable AI assistants like Claude to interact with WhatsApp through your personal account. All tools communicate with the Go bridge component via REST API.

## Tool Categories

### 🔍 Contact & Search Operations
- [`search_contacts`](#search_contacts) - Search for contacts by name or phone number

### 💬 Message Operations  
- [`list_messages`](#list_messages) - Retrieve messages with filtering and context
- [`get_message_context`](#get_message_context) - Get context around a specific message

### 🗂️ Chat Operations
- [`list_chats`](#list_chats) - List all chats with metadata
- [`get_chat`](#get_chat) - Get specific chat information by JID
- [`get_direct_chat_by_contact`](#get_direct_chat_by_contact) - Find direct chat with a contact
- [`get_contact_chats`](#get_contact_chats) - List all chats involving a contact  
- [`get_last_interaction`](#get_last_interaction) - Get most recent message with a contact

### 📤 Sending Operations
- [`send_message`](#send_message) - Send text messages
- [`send_file`](#send_file) - Send media files (images, videos, documents, raw audio)
- [`send_audio_message`](#send_audio_message) - Send audio files as voice messages

### 📥 Media Operations
- [`download_media`](#download_media) - Download media from messages

---

## Tool Detailed Documentation

### search_contacts

Search WhatsApp contacts by name or phone number.

**Parameters:**
- `query` (str): Search term to match against contact names or phone numbers

**Returns:**
- List of contacts with `phone_number`, `name`, and `jid` fields

**Example:**
```python
search_contacts("John")
# Returns: [{"phone_number": "1234567890", "name": "John Doe", "jid": "1234567890@s.whatsapp.net"}]
```

---

### list_messages

Retrieve WhatsApp messages with optional filtering, pagination, and context.

**Parameters:**
- `after` (str, optional): ISO-8601 date string - only return messages after this date
- `before` (str, optional): ISO-8601 date string - only return messages before this date  
- `sender_phone_number` (str, optional): Filter messages by sender phone number
- `chat_jid` (str, optional): Filter messages by specific chat JID
- `query` (str, optional): Search term to filter messages by content
- `limit` (int): Maximum number of messages to return (default: 20)
- `page` (int): Page number for pagination (default: 0)
- `include_context` (bool): Include surrounding messages for context (default: True)
- `context_before` (int): Number of messages before each match (default: 1)
- `context_after` (int): Number of messages after each match (default: 1)

**Returns:**
- List of message objects with full metadata and context

**Example:**
```python
list_messages(
    query="meeting",
    chat_jid="1234567890@s.whatsapp.net", 
    limit=10,
    include_context=True
)
```

---

### get_message_context

Get context around a specific message (messages before and after).

**Parameters:**
- `message_id` (str): ID of the target message
- `before` (int): Number of messages to include before target (default: 5)
- `after` (int): Number of messages to include after target (default: 5)

**Returns:**
- Object with `message`, `before`, and `after` arrays containing full message context

**Example:**
```python
get_message_context("msg123", before=3, after=3)
```

---

### list_chats

Get WhatsApp chats with filtering and sorting options.

**Parameters:**
- `query` (str, optional): Search term to filter chats by name or JID
- `limit` (int): Maximum number of chats to return (default: 20)
- `page` (int): Page number for pagination (default: 0)
- `include_last_message` (bool): Include last message in each chat (default: True)
- `sort_by` (str): Sort order - "last_active" or "name" (default: "last_active")

**Returns:**
- List of chat objects with metadata and last message info

**Example:**
```python
list_chats(query="work", sort_by="name", limit=50)
```

---

### get_chat

Get detailed information about a specific chat.

**Parameters:**
- `chat_jid` (str): The JID of the chat to retrieve
- `include_last_message` (bool): Include the last message (default: True)

**Returns:**
- Chat object with full metadata

**Example:**
```python
get_chat("1234567890@s.whatsapp.net", include_last_message=True)
```

---

### get_direct_chat_by_contact

Find a direct chat with a specific contact by phone number.

**Parameters:**
- `sender_phone_number` (str): Phone number to search for

**Returns:**
- Chat object for the direct conversation with that contact

**Example:**
```python
get_direct_chat_by_contact("1234567890")
```

---

### get_contact_chats

Get all chats involving a specific contact (both direct and group chats).

**Parameters:**
- `jid` (str): The contact's JID to search for
- `limit` (int): Maximum number of chats to return (default: 20)
- `page` (int): Page number for pagination (default: 0)

**Returns:**
- List of all chats involving the specified contact

**Example:**
```python
get_contact_chats("1234567890@s.whatsapp.net", limit=10)
```

---

### get_last_interaction

Get the most recent message involving a specific contact.

**Parameters:**
- `jid` (str): The JID of the contact to search for

**Returns:**
- String containing the most recent message with that contact

**Example:**
```python
get_last_interaction("1234567890@s.whatsapp.net")
```

---

### send_message

Send a text message to a person or group.

**Parameters:**
- `recipient` (str): Phone number (10-15 digits, no symbols) or JID
- `message` (str): The message text to send

**Returns:**
- Dictionary with `success` (bool) and `message` (str) status

**Recipient Formats:**
- Phone: `"1234567890"` 
- Contact JID: `"1234567890@s.whatsapp.net"`
- Group JID: `"123456789-123456789@g.us"`

**Example:**
```python
send_message("1234567890", "Hello! How are you?")
send_message("123456789-123456789@g.us", "Group message")
```

---

### send_file

Send a file (image, video, document, raw audio) to a recipient.

**Parameters:**
- `recipient` (str): Phone number or JID (same formats as send_message)
- `media_path` (str): Absolute path to the file to send

**Supported File Types:**
- Images: JPG, PNG, GIF, WebP
- Videos: MP4, MOV, AVI  
- Audio: MP3, WAV, OGG, M4A
- Documents: PDF, DOC, DOCX, TXT

**Returns:**
- Dictionary with `success` (bool) and `message` (str) status

**Example:**
```python
send_file("1234567890", "/path/to/document.pdf")
send_file("1234567890", "/path/to/image.jpg")
```

---

### send_audio_message

Send an audio file as a WhatsApp voice message (playable in-app).

**Parameters:**
- `recipient` (str): Phone number or JID
- `media_path` (str): Absolute path to the audio file

**Audio Requirements:**
- For best compatibility: `.ogg` Opus format
- With FFmpeg installed: Automatically converts MP3, WAV, etc. to Opus
- Without FFmpeg: Use `send_file` instead for raw audio files

**Returns:**
- Dictionary with `success` (bool) and `message` (str) status

**Example:**
```python
send_audio_message("1234567890", "/path/to/voice.wav")  # Auto-converts to Opus
send_audio_message("1234567890", "/path/to/voice.ogg")  # Direct send
```

---

### download_media

Download media from a WhatsApp message to local storage.

**Parameters:**
- `message_id` (str): The ID of the message containing media
- `chat_jid` (str): The JID of the chat containing the message

**Returns:**
- Dictionary with:
  - `success` (bool): Whether download succeeded
  - `message` (str): Status message  
  - `file_path` (str): Local path to downloaded file (if successful)

**Usage Notes:**
- Media metadata is stored in database, but files are downloaded on-demand
- Downloaded files are cached in the `store/` directory
- File paths can be used with other tools or opened directly

**Example:**
```python
result = download_media("msg123", "1234567890@s.whatsapp.net")
if result["success"]:
    file_path = result["file_path"]
    # Use file_path with other tools
```

---

## Usage Patterns

### Finding and Responding to Messages
```python
# Search for recent messages about "meeting"
messages = list_messages(query="meeting", limit=5)

# Get context around a specific message
context = get_message_context(messages[0]["id"], before=2, after=2)

# Send a response
send_message(messages[0]["chat_jid"], "Thanks for the meeting reminder!")
```

### Working with Media
```python
# List recent messages with media
messages = list_messages(limit=20)
media_messages = [m for m in messages if m.get("media_type")]

# Download media from a message
if media_messages:
    result = download_media(media_messages[0]["id"], media_messages[0]["chat_jid"])
    if result["success"]:
        print(f"Downloaded to: {result['file_path']}")
```

### Group Chat Management
```python
# Find group chats
groups = [chat for chat in list_chats() if chat["jid"].endswith("@g.us")]

# Send to a specific group
send_message("123456789-123456789@g.us", "Hello everyone!")

# Send file to group
send_file("123456789-123456789@g.us", "/path/to/presentation.pdf")
```

### Contact Interaction
```python
# Search for contacts
contacts = search_contacts("John")

# Get conversation history
if contacts:
    chat = get_direct_chat_by_contact(contacts[0]["phone_number"])
    messages = list_messages(chat_jid=chat["jid"], limit=10)
    
    # Send a message
    send_message(contacts[0]["jid"], "Hi John!")
```

## Error Handling

All tools return structured responses with error information:

```python
result = send_message("invalid", "test")
if not result["success"]:
    print(f"Error: {result['message']}")
```

Common error scenarios:
- Invalid recipient format
- File not found or unsupported type
- Network connection issues
- WhatsApp session expired (need to re-authenticate)
- Message too long (>4096 characters)

## Security Considerations

- All operations require active WhatsApp session (QR code authentication)
- Messages and media are stored locally in SQLite database
- No cloud storage or external API calls
- File validation prevents path traversal attacks
- Media downloads are cached and reused efficiently